from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = REPO_ROOT / "data" / "logs.jsonl"
CONFIG_PATH = REPO_ROOT / "config" / "dashboard.yaml"
HTML_PATH = REPO_ROOT / "app" / "dashboard.html"


def percentile(values: list[float], p: int) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = round((len(ordered) - 1) * p / 100)
    return float(ordered[index])


def _minute_key(timestamp: datetime) -> str:
    return timestamp.replace(second=0, microsecond=0).isoformat()


def build_overview(now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    start = now - timedelta(minutes=60)
    minutes = [
        (start + timedelta(minutes=index)).replace(second=0, microsecond=0)
        for index in range(60)
    ]
    labels = [minute.strftime("%H:%M") for minute in minutes]
    bins: dict[str, list[dict]] = defaultdict(list)
    rows: list[dict] = []
    if LOG_PATH.exists():
        for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
            try:
                record = json.loads(line)
                timestamp = datetime.fromisoformat(record["ts"].replace("Z", "+00:00"))
            except (ValueError, KeyError, TypeError, json.JSONDecodeError):
                continue
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            if start <= timestamp <= now:
                rows.append(record)
                bins[_minute_key(timestamp)].append(record)

    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))["dashboard"]
    thresholds = {panel["id"]: panel["threshold"]["value"] for panel in config["panels"]}
    secondary_thresholds = {
        panel["id"]: panel["secondary_threshold"]["value"]
        for panel in config["panels"] if "secondary_threshold" in panel
    }

    def values_for(event: str, field: str) -> list[float]:
        return [
            float(record[field])
            for record in rows
            if record.get("event") == event and isinstance(record.get(field), (int, float))
        ]

    latency = values_for("response_sent", "latency_ms")
    ttft = values_for("response_sent", "ttft_ms")
    received = sum(row.get("event") == "request_received" for row in rows)
    failed = sum(row.get("event") == "request_failed" for row in rows)
    tool_rows = [row for row in rows if isinstance(row.get("tool_success"), bool)]
    retrieval_success = (
        100 * sum(row["tool_success"] for row in tool_rows) / len(tool_rows)
        if tool_rows
        else 0.0
    )
    total_cost = sum(values_for("response_sent", "cost_usd"))
    quality = values_for("response_sent", "quality_score")
    input_tokens = values_for("response_sent", "tokens_in")
    output_tokens = values_for("response_sent", "tokens_out")

    series = {
        "latency_p95": [], "ttft_p95": [], "traffic": [], "error_rate": [],
        "cost": [], "tokens_in": [], "tokens_out": [], "quality": [],
        "retrieval_success": [],
    }
    for minute in minutes:
        bucket = bins.get(_minute_key(minute), [])
        response_rows = [row for row in bucket if row.get("event") == "response_sent"]
        request_count = sum(row.get("event") == "request_received" for row in bucket)
        failed_count = sum(row.get("event") == "request_failed" for row in bucket)
        tools = [row for row in bucket if isinstance(row.get("tool_success"), bool)]

        def bucket_values(field: str) -> list[float]:
            return [float(row[field]) for row in response_rows if isinstance(row.get(field), (int, float))]

        series["latency_p95"].append(percentile(bucket_values("latency_ms"), 95) if response_rows else None)
        series["ttft_p95"].append(percentile(bucket_values("ttft_ms"), 95) if response_rows else None)
        series["traffic"].append(request_count)
        series["error_rate"].append((100 * failed_count / request_count) if request_count else None)
        series["cost"].append(sum(series["cost"]) + sum(float(row.get("cost_usd", 0)) for row in response_rows))
        series["tokens_in"].append(sum(series["tokens_in"]) + sum(float(row.get("tokens_in", 0)) for row in response_rows))
        series["tokens_out"].append(sum(series["tokens_out"]) + sum(float(row.get("tokens_out", 0)) for row in response_rows))
        series["quality"].append(
            sum(bucket_values("quality_score")) / len(bucket_values("quality_score"))
            if bucket_values("quality_score") else None
        )
        series["retrieval_success"].append(
            100 * sum(row["tool_success"] for row in tools) / len(tools) if tools else None
        )

    return {
        "title": config["title"],
        "time_range_minutes": config["time_range_minutes"],
        "refresh_seconds": config["refresh_seconds"],
        "updated_at": now.isoformat(),
        "labels": labels,
        "series": series,
        "summary": {
            "latency_p50_ms": percentile(latency, 50),
            "latency_p95_ms": percentile(latency, 95),
            "latency_p99_ms": percentile(latency, 99),
            "ttft_p95_ms": percentile(ttft, 95),
            "requests": received,
            "error_rate_pct": (100 * failed / received) if received else 0,
            "retrieval_success_pct": retrieval_success,
            "cost_usd": total_cost,
            "tokens_in": sum(input_tokens),
            "tokens_out": sum(output_tokens),
            "quality_avg": sum(quality) / len(quality) if quality else 0,
        },
        "thresholds": thresholds,
        "secondary_thresholds": secondary_thresholds,
    }


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/overview":
            body = json.dumps(build_overview(), ensure_ascii=False).encode("utf-8")
            content_type = "application/json; charset=utf-8"
        elif path == "/":
            body = HTML_PATH.read_bytes()
            content_type = "text/html; charset=utf-8"
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    sys.path.insert(0, str(REPO_ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", 8501), DashboardHandler)
    print("Dashboard: http://127.0.0.1:8501 (refreshes every 30 seconds)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Dashboard stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
