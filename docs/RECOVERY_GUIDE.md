# Hướng dẫn tiếp tục bài Monitoring & LLMOps

Cập nhật: 30/09/2026. Bản này phản ánh code, Langfuse và workload đã chạy thật, tránh phải dò lại lịch sử chat.

## Mục tiêu bài

Điều tra một sự cố theo luồng `Metrics → Logs → Traces → Root cause`: dùng metric tìm triệu chứng, correlation ID tìm log của request, trace xác định span gây chậm/lỗi, rồi giải thích root cause bằng bằng chứng.

## Đã hoàn tất

- Correlation ID, structured logging và PII scrub; 26 tests đã pass. Log validator sau workload cuối: 100/100 trên 273 records, 119 correlation IDs, không thiếu field/context và không phát hiện PII leak.
- Dashboard runtime local có 6 panel; dashboard contract validator pass 6/6.
- Langfuse đã nhận 10 baseline v1 traces, 10 candidate v2 traces, 10 production v2 traces. Metadata xác nhận prompt managed. Prompt production đã rollback về v1; candidate vẫn v2.
- Challenge `day13-k4-l3b-monitoring-llmops-v1` đã chạy 5 request; latency mỗi request 2,653–2,656 ms, median 2,654 ms, threshold 2,000 ms. Root cause là `rag_slow` thêm 2,5 giây ở retrieval. Incident đã disable.
- Report đã điền họ tên Nguyễn Quang Hữu, MSSV 2A202602756, repo URL, kết quả challenge và trace IDs mẫu.

## File chính và tình trạng

| File | Trạng thái |
|---|---|
| `app/middleware.py`, `app/main.py` | Correlation ID, log/response và endpoints incident đã triển khai. |
| `app/logging_config.py`, `app/pii.py` | PII scrub trước khi ghi/render. |
| `app/agent.py`, `app/mock_rag.py`, `app/mock_llm.py`, `app/tracing.py` | Root + retrieval + generation; safe trace metadata. |
| `app/prompt_management.py` | Prompt Langfuse theo name/label, local fallback nếu fetch lỗi. |
| `config/dashboard.yaml`, `config/slo.yaml`, `config/alert_rules.yaml` | 6 panel, SLO/error budget và 3 alert đã khai báo. |
| `scripts/load_test.py` | Load test thường/challenge, hỗ trợ `--base-url`. |
| `scripts/dashboard.py`, `app/dashboard.html` | Dashboard local tại `http://127.0.0.1:8501`. |
| `submission/REPORT.md` | Report đã cập nhật; còn ảnh và commit SHA. |
| `submission/evidence/` | Text evidence đã có; ảnh Langfuse, dashboard và challenge còn cần chụp. |

## Langfuse

- Prompt: `day13-chat`; v1=`baseline` + `production`, v2=`candidate`; đã promote production sang v2 và rollback về v1.
- `.env` cục bộ hiện có `LANGFUSE_PROMPT_NAME=day13-chat`, `LANGFUSE_PROMPT_LABEL=production`; server lab đã dừng.
- Langfuse API xác nhận candidate/production v2; sau rollback đã gửi một request và xác nhận trace `production` v1: `381a0be50c4f2d22b3bd10f71bea2e34`.
- Không chia sẻ hoặc commit `.env`, key/secret. Challenge file ở `config/challenge.json` bị `.gitignore` cố ý; không commit đề.
- Hướng dẫn ảnh từng màn hình và bước chạy lại trace ở [LANGFUSE_HANDOFF.md](LANGFUSE_HANDOFF.md).

## Challenge đã điều tra

- ID: `day13-k4-l3b-monitoring-llmops-v1`.
- Thời gian: 30/09/2026 05:40:20–05:40:33 UTC.
- Triệu chứng: cả 5 request đều HTTP 200 nhưng trên 2,000 ms; retrieval success 100%, TTFT khoảng 50 ms.
- Correlation IDs: `req-dfbf3b18`, `req-e626e9fa`, `req-24101db0`, `req-ceaaa4f1`, `req-fbc5f6ed`.
- Trace đại diện: `8673ac582d602ab117129cd72eec65d6`, correlation `req-24101db0`; retrieval là span chậm.
- Root cause: `time.sleep(2.5)` khi cờ `rag_slow` bật trong `app/mock_rag.py`. Đã gọi disable và health xác nhận incident off.
- Output: `submission/evidence/12-incident-metric.json`, `13-incident-load.txt`, `13-incident-log.txt`, `14-incident-trace.txt`.

## Việc còn lại theo thứ tự

1. Chụp ảnh 06–10 của Langfuse; ghi tên project nhìn thấy. Hướng dẫn chi tiết trong `docs/LANGFUSE_HANDOFF.md`.
2. (Tuỳ chọn) Gửi thêm workload `production` nếu cần trace mới; trace rollback đã được xác nhận và ghi trong report.
3. Chụp ảnh dashboard 11, challenge metric 12, log 13 và trace 14; để ảnh vào `submission/evidence/`.
4. Chụp ảnh; tên project và trace rollback đã có trong `submission/REPORT.md`. Điền commit SHA sau commit cuối.
5. Kiểm tra `git status`, giữ `.env` và `config/challenge.json` ngoài commit; không xóa `.idea/` hay file chưa được rà soát.

## Bắt đầu nhanh

Chạy dashboard:

```powershell
.\.venv\Scripts\python.exe scripts/dashboard.py
```

Mở `http://127.0.0.1:8501`. Để chạy API, dùng hướng dẫn trong `docs/LANGFUSE_HANDOFF.md`, kiểm tra `/health` trước workload. Tracing cần `tracing_enabled=true`; nếu metadata ghi `local-fallback`, không tính đó là trace Langfuse.
