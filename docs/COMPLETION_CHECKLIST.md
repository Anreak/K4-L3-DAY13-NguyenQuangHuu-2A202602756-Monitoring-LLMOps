# Danh sách file cần hoàn thiện

Trạng thái cập nhật ngày 30/09/2026 cho repo K4-L3B Day 13. Tài liệu này chỉ liệt kê phần còn lại thật sự; chi tiết ảnh nằm trong [LANGFUSE_HANDOFF.md](LANGFUSE_HANDOFF.md).

## Đã làm và có thể kiểm tra

| File/khu vực | Trạng thái | Evidence |
|---|---|---|
| `app/middleware.py`, `app/main.py` | Correlation ID vào log, response header/body; endpoint incident hoạt động. | `submission/evidence/04-structured-log.txt`, `13-incident-log.txt` |
| `app/logging_config.py`, `app/pii.py` | Scrub PII đệ quy trước khi ghi log/render. | `submission/evidence/05-pii-redaction-runtime.txt` |
| `app/agent.py`, `app/mock_rag.py`, `app/mock_llm.py`, `app/tracing.py` | Root + retrieval + generation; trace không capture raw input/output. | `submission/evidence/06-langfuse-traces.txt`, `14-incident-trace.txt` |
| `app/prompt_management.py`, `.env` local | Prompt `day13-chat`; `.env` hiện trỏ label `production`. Không commit `.env`. | `submission/evidence/09-langfuse-version-traces.txt` |
| Langfuse | v1 baseline; v2 candidate; promote `production` sang v2, chạy 10 trace, rollback label về v1 và xác nhận thêm trace v1 sau rollback. | `submission/evidence/06-langfuse-traces.txt`, `09-langfuse-version-traces.txt`, `10-production-v1-rollback-trace.txt` |
| `scripts/load_test.py` | Có `--base-url`; baseline 10 request, candidate 10, production v2 10 đều HTTP 200. | `submission/evidence/06-baseline-load.txt`, `07-candidate-load.txt`, `08-production-v2-load.txt` |
| `config/challenge.json` (ignored) | Challenge chính thức đã chạy; retrieval latency vượt ngưỡng; incident đã tắt lại. Không đưa file challenge vào Git. | `submission/evidence/12-incident-metric.json`, `13-incident-load.txt`, `13-incident-log.txt`, `14-incident-trace.txt` |
| Dashboard/SLO/alerts | Contract 6/6; SLO/error budget và 3 alerts/runbooks đã điền. | `submission/evidence/03-dashboard-validator.txt`, `config/`, `docs/alerts.md` |
| Validators | Log validator 100/100 trên 273 records, không thiếu field/context, không leak PII. | `submission/evidence/02-log-validator.txt` |
| `submission/REPORT.md` | Họ tên, MSSV, repo URL và kết quả runtime đã điền; phần còn thiếu được ghi rõ. | Mở report để rà soát |

## Còn cần bạn chụp hoặc xác nhận

1. **Ảnh Langfuse (06–10):** Traces list; trace waterfall; trace metadata; prompt v1/v2; production v2 sau promote; production v1 sau rollback. Hướng dẫn từng ảnh ở `docs/LANGFUSE_HANDOFF.md`. Không chụp màn hình API Keys.
2. **Ảnh dashboard (11):** Mở dashboard local và chụp đủ sáu panel, time range, đơn vị, thresholds/SLO.
3. **Ảnh challenge (12–14):** Chụp metric; log có correlation ID; trace cùng correlation ID, mở rộng retrieval span.
4. **Project Langfuse:** Xác nhận đúng tên project cá nhân nhìn thấy ở đầu trang; không gửi key/secret.
5. **Project Langfuse:** Tên `day13-k4-l3b-2A202602756` đã đọc từ API; ảnh Langfuse cần hiện tên project để người chấm nhận diện.
6. **`submission/REPORT.md`:** Tên project và trace rollback đã điền. Chụp/lưu ảnh rồi điền commit SHA sau commit cuối.

## Lưu ý khi nộp

- `config/challenge.json` được `.gitignore` cố ý bỏ qua; không force-add hoặc đưa đề challenge lên Git.
- Không commit `.env`, Langfuse keys, raw PII, hay log runtime `data/logs.jsonl`.
- Report chưa thể tick hoàn tất cho đến khi ảnh evidence được lưu và các đường dẫn/commit SHA khớp.
