# Báo cáo cá nhân — K4-L3B Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** Nguyễn Quang Hữu
- **MSSV:** 2A202602756
- **Lớp:** K4-L3B
- **Repository URL:** https://github.com/Anreak/K4-L3-DAY13-NguyenQuangHuu-2A202602756-Monitoring-LLMOps
- **Commit SHA:** `74573328ca168093d14a3161cf4d98545d29c421`
- **Challenge ID:** `day13-k4-l3b-monitoring-llmops-v1`
- **Tên project Langfuse cá nhân:** `day13-k4-l3b-2A202602756` (xác nhận qua API project của credentials đang cấu hình).

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Có thể đổi tên hoặc dùng nhiều ảnh nếu cần.

| Evidence | Đường dẫn |
|---|---|
| Pytest cuối | `evidence/01-pytest.png` |
| Log validator | `evidence/02-log-validator.png` |
| Dashboard validator | `evidence/03-dashboard-validator.png` |
| Structured log | `evidence/04-structured-log.png` |
| PII redaction | `evidence/05-pii-redaction.png` |
| Langfuse trace list | `evidence/06-trace-list.png` |
| Trace waterfall | `evidence/07-trace-waterfall.png` |
| Trace metadata | `evidence/08a.png` |
| Generation model/token/cost | `evidence/08b.png` |
| Prompt versions | `evidence/09-prompt-versions.png` |
| Production v2 sau promote | `evidence/10a.png` (v2 có label `production`) |
| Production v1 sau rollback | `evidence/10b.png` |
| Dashboard runtime | `evidence/11-dashboard-overview.png` |
| Incident metric | `evidence/12-incident-metric.png` (dashboard 06:40–07:39 UTC; chưa bao gồm challenge lúc khoảng 05:40 UTC, cần chụp lại đúng time range) |
| Incident log | `evidence/13-incident-log.png` |
| Incident trace | `evidence/14-incident-trace.png` (trace challenge, `correlation_id=req-24101db0`) |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | Chưa ghi baseline | 100/100; 293 records, 129 correlation IDs | 0 trường thiếu, 0 context enrichment thiếu, 0 leak PII |
| `validate_dashboard.py` | Chưa ghi baseline | 6/6 panel | Contract hợp lệ; runtime ở ảnh 11; ảnh 12 cần chụp lại đúng time range của challenge |
| `pytest` | Chưa ghi baseline | 26 passed | Ảnh terminal: `evidence/01-pytest.png` |
| Số traces hợp lệ | Chưa ghi baseline | Tối thiểu 36 root traces / 108 observations đã xác minh trước đó | Ảnh trace list hiện hiển thị 104 root observations trong khoảng thời gian đang chọn |
| Số PII leak | Chưa ghi baseline | 0 theo log validator | Smoke test local cũng xác nhận mẫu email/điện thoại/thẻ đã scrub |
| Latency P95 / TTFT P95 | Chưa ghi baseline riêng | Dashboard overview: P95 1,451 ms, TTFT P95 51 ms; challenge: 5/5 request 2,653–2,656 ms | Challenge median 2,654 ms vượt ngưỡng 2,000 ms; ảnh dashboard 12 hiện tại chưa nằm trong challenge time range |
| Retrieval success rate | Chưa ghi baseline | 100% (5/5 challenge request) | Cả năm log `response_sent` đều có `tool_success=true`; retrieval bị chậm nhưng không lỗi |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:** Middleware nhận `x-request-id` đúng định dạng hoặc sinh `req-<8-hex>`, rồi trả ID ở header và response body. Smoke test local dùng `req-9b6c9451`; ID nằm trong cả hai log event. Langfuse root metadata ghi cùng correlation ID.
- **Các metadata được ghi vào structured log:** `user_id_hash`, `session_id` đã scrub, `feature` đã scrub, `model`, `env`, `correlation_id`; event kết thúc request còn có latency, TTFT, token, cost, quality và retrieval status.
- **Cách bảo đảm PII được scrub trước khi ghi:** `scrub_event` chạy trước file writer/JSON renderer và đệ quy qua chuỗi trong dict/list/tuple. Trace metadata cũng scrub `session_id` và `feature`; raw user ID chỉ lưu dạng hash.
- **Cách kiểm chứng kết quả:** Structured log có `correlation_id`, model, latency và trạng thái retrieval; ảnh PII cho thấy email/điện thoại/thẻ mẫu đã được thay bằng token `[REDACTED_...]`. Xem `evidence/04-structured-log.png` và `evidence/05-pii-redaction.png`.

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:** Langfuse API trả 45 observations tương ứng 15 root traces trong lượt baseline/challenge; 60 observations nữa tương ứng 20 root traces candidate/production v2; thêm một trace production v1 sau rollback. Metadata chứa các correlation ID khớp log workload.
- **Cấu trúc root/retrieval/generation observations:** Trace `89b119758e2f145c28af4b4e324ff876` có root `lab-agent-run` và hai child `retrieval`, `generation`. Ảnh `evidence/07-trace-waterfall.png` cho thấy cây; ảnh `evidence/08b.png` cho thấy generation dùng model `claude-sonnet-4-5`, tổng 196 tokens và cost `$0.002604`.
- **Cách nối trace với log:** Ảnh metadata `evidence/08a.png` cho thấy trace `89b119758e2f145c28af4b4e324ff876` có `correlation_id=req-035d7711`, prompt `day13-chat`, label `production`, version 1 và `prompt_source=langfuse`.
- **Prompt name:** `day13-chat`; API xác nhận trace dùng prompt managed (`prompt_source=langfuse`).
- **Version/label baseline:** Version 1 / `baseline`; đã xác minh trên trace Langfuse.
- **Version/label candidate:** Version 2 / `candidate`; đã tạo 10 request và Langfuse trả 10 root traces với `prompt_source=langfuse`.
- **Trace ID của mỗi version:** Baseline v1: `8673ac582d602ab117129cd72eec65d6`, correlation `req-24101db0`; candidate v2: `3429cd635c5d3eca348722f8a8c9ade7`, correlation `req-a80d7722`; production v2: `f56ab203e00fceff172000d47a3d06cf`, correlation `req-ff29a25e`; production v1 sau rollback: `381a0be50c4f2d22b3bd10f71bea2e34`, correlation `req-4fcce137`. Các ID đã được xác minh trước đó qua Langfuse API.
- **Cách promote và rollback `production`:** Đã chuyển `production` sang version 2, sau đó rollback về version 1. `evidence/10a.png` cho thấy trạng thái v2 có `production` (sau promote); `evidence/10b.png` cho thấy sau rollback, v1 có `production` và v2 còn `candidate`.

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:** Dashboard local đọc `data/logs.jsonl`, hiển thị 60 phút gần nhất và tự refresh mỗi 30 giây. Validator đạt 6/6. Ảnh `evidence/11-dashboard-overview.png` hiển thị sáu panel, 11 requests, P50 153 ms, P95 1,451 ms, TTFT P95 51 ms, error 0%, retrieval success 100%, cost `$0.0224`, quality 0.88.
- **SLO và lý do chọn:** 99.5% request hoàn tất trong 3 giây trong cửa sổ 28 ngày; ngưỡng theo lab và cần hiệu chỉnh bằng baseline production.
- **Cách tính error budget:** 0.5% budget; tối đa 50 request không đạt trong 10,000 request.
- **Ba alert và runbook tương ứng:** `HighLatencyP95`, `ElevatedRequestFailures`, `QualityOrCostGuardrail`; runbook Metrics → Logs → Traces tại `docs/alerts.md`.

> Ví dụ cách viết error budget: "SLO 99.5% trong 28 ngày nghĩa là error budget 0.5%. Nếu workload có 10,000 request thì tối đa 50 request được phép lỗi hoặc chậm hơn ngưỡng SLO."

## 7. Điều tra challenge

- **Challenge ID:** `day13-k4-l3b-monitoring-llmops-v1`.
- **Khoảng thời gian điều tra:** 2026-09-30 05:40:20–05:40:33 UTC (12:40:20–12:40:33 giờ Việt Nam), theo log challenge trong `evidence/13-incident-log.png`.
- **Triệu chứng từ metrics:** 5/5 request challenge thành công; latency 2,653–2,656 ms, median 2,654 ms; vượt ngưỡng challenge 2,000 ms. TTFT khoảng 50 ms.
- **Log line và correlation ID liên quan:** Ảnh `evidence/13-incident-log.png` hiển thị năm correlation ID challenge: `req-dfbf3b18`, `req-e626e9fa`, `req-24101db0`, `req-ceaaa4f1`, `req-fbc5f6ed`.
- **Trace ID và span gây ảnh hưởng:** Trace challenge `8673ac582d602ab117129cd72eec65d6`, correlation `req-24101db0`; ảnh `evidence/14-incident-trace.png` hiển thị root `lab-agent-run` (2.65 giây), child `retrieval` (2.50 giây) và `generation` (0.15 giây), cùng metadata `session_id=k4-l3b-challenge-s01`, `prompt_source=langfuse`, prompt version 1 / `baseline`. Đây là bằng chứng trace cho thấy retrieval gây phần lớn độ trễ.
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
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:** Ảnh metric 12 chưa khớp thời gian challenge; ảnh trace 14 chưa khớp correlation ID và không có child retrieval span. Cần chụp lại hai ảnh này. Commit SHA cuối cần điền sau khi commit bản nộp.

## 9. Checklist trước khi nộp

- [ ] Kết quả và evidence thuộc commit SHA cuối.
- [ ] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [ ] Incident evidence nối đúng metric → log → trace (còn thiếu ảnh metric 12 và trace 14 hợp lệ).
- [ ] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [ ] Repository chạy lại được theo README.
- [ ] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [ ] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.
