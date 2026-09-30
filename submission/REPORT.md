# Báo cáo cá nhân — K4-L3B Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** Nguyễn Quang Hữu
- **MSSV:** 2A202602756
- **Lớp:** K4-L3B
- **Repository URL:** https://github.com/Anreak/K4-L3-DAY13-NguyenQuangHuu-2A202602756-Monitoring-LLMOps
- **Commit SHA cuối:**
- **Challenge ID:** `day13-k4-l3b-monitoring-llmops-v1`
- **Tên project Langfuse cá nhân:** `day13-k4-l3b-2A202602756` (xác nhận qua API project của credentials đang cấu hình).

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Có thể đổi tên hoặc dùng nhiều ảnh nếu cần.

| Evidence | Đường dẫn |
|---|---|
| Pytest cuối | `evidence/01-pytest.txt` |
| Log validator | `evidence/02-log-validator.txt` |
| Dashboard validator | `evidence/03-dashboard-validator.txt` |
| Structured log | `evidence/04-structured-log.txt` |
| PII redaction | `evidence/05-pii-redaction-runtime.txt` |
| Baseline load | `evidence/06-baseline-load.txt` |
| Langfuse trace list/metadata (text) | `evidence/06-langfuse-traces.txt` |
| Candidate load | `evidence/07-candidate-load.txt` |
| Production v2 load | `evidence/08-production-v2-load.txt` |
| Candidate/production v2 Langfuse trace IDs | `evidence/09-langfuse-version-traces.txt` |
| Production v1 rollback workload (DNS fallback; not a managed trace) | `evidence/10-production-v1-rollback-load.txt` |
| Production v1 trace after rollback | `evidence/10-production-v1-rollback-trace.txt` |
| Trace list | `evidence/06-trace-list.png` |
| Trace waterfall | `evidence/07-trace-waterfall.png` |
| Trace metadata | `evidence/08-trace-metadata.png` |
| Prompt versions | `evidence/09-prompt-versions.png` |
| Prompt rollback sau promote | `evidence/10a-prompt-production-v2.png` |
| Prompt rollback sau khi quay về v1 | `evidence/10b-prompt-production-v1.png` |
| Dashboard runtime | `evidence/11-dashboard-overview.png` |
| Incident metric | `evidence/12-incident-metric.png` |
| Incident metric snapshot (JSON) | `evidence/12-incident-metric.json` |
| Incident workload | `evidence/13-incident-load.txt` |
| Incident log (text, scrubbed fields only) | `evidence/13-incident-log.txt` |
| Incident log screenshot | `evidence/13-incident-log.png` |
| Incident trace | `evidence/14-incident-trace.png` |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | Chưa ghi baseline | 100/100; 273 records, 119 correlation IDs | 0 trường thiếu, 0 context enrichment thiếu, 0 leak PII |
| `validate_dashboard.py` | Chưa ghi baseline | 6/6 panel | Contract hợp lệ; dashboard runtime cần ảnh riêng |
| `pytest` | Chưa ghi baseline | 26 passed | Chạy trên working tree hiện tại |
| Số traces hợp lệ | Chưa ghi baseline | Tối thiểu 36 root traces / 108 observations | 15 baseline/challenge + 10 candidate v2 + 10 production v2 + 1 production v1 sau rollback |
| Số PII leak | Chưa ghi baseline | 0 theo log validator | Smoke test local cũng xác nhận mẫu email/điện thoại/thẻ đã scrub |
| Latency P95 / TTFT P95 | Chưa ghi baseline | Snapshot local 15 request: P95 5,650 ms; TTFT P95 51 ms | P95 tổng bị ảnh hưởng bởi lần fetch prompt đầu tiên khi cache lạnh; challenge riêng: 5/5 request 2,653–2,656 ms |
| Retrieval success rate | Chưa ghi baseline | 100% (5/5 challenge request) | Cả năm log `response_sent` đều có `tool_success=true`; retrieval bị chậm nhưng không lỗi |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:** Middleware nhận `x-request-id` đúng định dạng hoặc sinh `req-<8-hex>`, rồi trả ID ở header và response body. Smoke test local dùng `req-9b6c9451`; ID nằm trong cả hai log event. Langfuse root metadata ghi cùng correlation ID.
- **Các metadata được ghi vào structured log:** `user_id_hash`, `session_id` đã scrub, `feature` đã scrub, `model`, `env`, `correlation_id`; event kết thúc request còn có latency, TTFT, token, cost, quality và retrieval status.
- **Cách bảo đảm PII được scrub trước khi ghi:** `scrub_event` chạy trước file writer/JSON renderer và đệ quy qua chuỗi trong dict/list/tuple. Trace metadata cũng scrub `session_id` và `feature`; raw user ID chỉ lưu dạng hash.
- **Cách kiểm chứng kết quả:** 10 baseline request trả HTTP 200; các trường nhạy cảm trong sample được scrub trong structured log. Sau đó kiểm tra trên Langfuse bằng correlation ID và metadata, không lấy nội dung input/output. Output: `evidence/04-structured-log.txt`, `evidence/05-pii-redaction-runtime.txt`, `evidence/06-baseline-load.txt`.

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:** Langfuse API trả 45 observations tương ứng 15 root traces trong lượt baseline/challenge; 60 observations nữa tương ứng 20 root traces candidate/production v2; thêm một trace production v1 sau rollback. Metadata chứa các correlation ID khớp log workload.
- **Cấu trúc root/retrieval/generation observations:** Đã xác minh root `lab-agent-run` có child `retrieval` kiểu `RETRIEVER` và `generation` kiểu `GENERATION`. Capture input/output bị tắt; generation có model, token usage và cost.
- **Cách nối trace với log:** Metadata root có `correlation_id`, trùng với `correlation_id` trong `request_received`/`response_sent`. Trace challenge mẫu: `8673ac582d602ab117129cd72eec65d6`; correlation ID `req-24101db0`.
- **Prompt name:** `day13-chat`; API xác nhận trace dùng prompt managed (`prompt_source=langfuse`).
- **Version/label baseline:** Version 1 / `baseline`; đã xác minh trên trace Langfuse.
- **Version/label candidate:** Version 2 / `candidate`; đã tạo 10 request và Langfuse trả 10 root traces với `prompt_source=langfuse`.
- **Trace ID của mỗi version:** Baseline v1: `8673ac582d602ab117129cd72eec65d6`, correlation `req-24101db0`; candidate v2: `3429cd635c5d3eca348722f8a8c9ade7`, correlation `req-a80d7722`; production v2: `f56ab203e00fceff172000d47a3d06cf`, correlation `req-ff29a25e`; production v1 sau rollback: `381a0be50c4f2d22b3bd10f71bea2e34`, correlation `req-4fcce137`. Danh sách v2 ở `evidence/09-langfuse-version-traces.txt`.
- **Cách promote và rollback `production`:** Đã chuyển `production` sang version 2, chạy 10 request, rồi rollback về version 1. Langfuse API xác nhận sau rollback: baseline=1, production=1, candidate=2. Trace sau rollback mới xác nhận `production`, version 1, `prompt_source=langfuse`; xem `evidence/10-production-v1-rollback-trace.txt`. Ảnh 10a/10b còn cần chụp trong UI.

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:** Code dashboard local đọc `data/logs.jsonl`, time range 60 phút, refresh 30 giây; contract validator đạt 6/6. Snapshot trong run 15 request: traffic 15, latency P50 154 ms/P95 5,650 ms, TTFT P95 51 ms, error 0; cần chụp ảnh dashboard runtime.
- **SLO và lý do chọn:** 99.5% request hoàn tất trong 3 giây trong cửa sổ 28 ngày; ngưỡng theo lab và cần hiệu chỉnh bằng baseline production.
- **Cách tính error budget:** 0.5% budget; tối đa 50 request không đạt trong 10,000 request.
- **Ba alert và runbook tương ứng:** `HighLatencyP95`, `ElevatedRequestFailures`, `QualityOrCostGuardrail`; runbook Metrics → Logs → Traces tại `docs/alerts.md`.

> Ví dụ cách viết error budget: "SLO 99.5% trong 28 ngày nghĩa là error budget 0.5%. Nếu workload có 10,000 request thì tối đa 50 request được phép lỗi hoặc chậm hơn ngưỡng SLO."

## 7. Điều tra challenge

- **Challenge ID:** `day13-k4-l3b-monitoring-llmops-v1`.
- **Khoảng thời gian điều tra:** 2026-09-30 05:40:20–05:40:33 UTC (12:40:20–12:40:33 giờ Việt Nam).
- **Triệu chứng từ metrics:** 5/5 request thành công nhưng latency 2,653–2,656 ms, median 2,654 ms; vượt ngưỡng challenge 2,000 ms. TTFT khoảng 50 ms.
- **Log line và correlation ID liên quan:** `response_sent`, feature `monitoring`, tool `retrieval`, `tool_success=true`; IDs: `req-dfbf3b18`, `req-e626e9fa`, `req-24101db0`, `req-ceaaa4f1`, `req-fbc5f6ed`. Đối chiếu trong `evidence/13-incident-log.txt`.
- **Trace ID và span gây ảnh hưởng:** Trace mẫu `8673ac582d602ab117129cd72eec65d6`, root `38ac69e6708f3e83`, retrieval `8565a0999def3e6e`, generation `0a6d1a2f0a46a497`; correlation `req-24101db0`.
- **Root cause:** `rag_slow` cố ý chèn `time.sleep(2.5)` trong `app/mock_rag.py` retrieval; phần generation chỉ khoảng 150 ms.
- **Fix action:** Gọi endpoint disable incident; health sau chạy xác nhận `rag_slow=false`.
- **Preventive measure:** Giữ cảnh báo latency P95, điều tra theo Metrics → Logs → Traces, và luôn xác nhận incident đã disable sau workload.

> Gợi ý cách viết ngắn, không thay cho evidence thực tế: "Metric cho thấy `[latency/error/cost/quality]` bất thường trong `[khoảng thời gian]`. Log line `[event]` có `correlation_id=[...]` đại diện cho request bị ảnh hưởng. Trace cùng `correlation_id` cho thấy span `[retrieval/generation/prompt/tool]` có dấu hiệu `[chậm/lỗi/token tăng]`. Root cause là `[nguyên nhân suy ra từ evidence]`. Fix action là `[hành động khôi phục]`; preventive measure là `[alert/runbook/test/guardrail để ngăn tái diễn]`."

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:** Tắt capture input/output trong trace và scrub metadata/log trước khi ghi để tránh lộ PII.
- **Một lỗi/blocker đã gặp:** Cấu hình prompt name ban đầu không khớp Langfuse; kết nối Langfuse từ môi trường chạy đôi lúc timeout.
- **Cách tìm nguyên nhân và xử lý:** Đối chiếu prompt label/version trực tiếp qua API, sửa prompt canonical thành `day13-chat`, sau đó kiểm tra trace metadata và correlation ID.
- **Cách hiểu luồng Metrics → Logs → Traces:** Metric cho biết request chậm; log tìm đúng correlation ID; trace xác định retrieval là span bị chậm.
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:** Label/version giúp truy vết prompt đã chạy; token/cost đo ảnh hưởng; SLO phát hiện lệch chuẩn; production label cho phép rollback mà không đổi code.
- **Điều quan trọng nhất đã học:** Correlation ID làm cầu nối giữa ba lớp Metrics, Logs, Traces.
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:** Chưa chụp ảnh Langfuse/dashboard và chưa điền commit SHA cuối. Cần hoàn thành các ảnh evidence trước khi nộp.

## 9. Checklist trước khi nộp

- [ ] Kết quả và evidence thuộc commit SHA cuối.
- [ ] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [ ] Incident evidence nối đúng metric → log → trace.
- [ ] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [ ] Repository chạy lại được theo README.
- [ ] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [ ] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.
