# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert mẫu để tham khảo

Ví dụ dưới đây minh họa mức độ cụ thể cần có. Học viên không cần copy nguyên, nhưng ba alert trong bài nộp nên rõ ràng tương tự: điều kiện là gì, kéo dài bao lâu, ảnh hưởng tới user ra sao và người trực cần kiểm tra gì trước.

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: latency P95 của `response_sent.latency_ms`
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 3000ms` trong 5 phút
- Ảnh hưởng tới người dùng: người dùng phải chờ lâu hơn trước khi nhận câu trả lời
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard latency để xác nhận P95/P99 và khoảng thời gian tăng.
  2. Lọc `data/logs.jsonl` trong khoảng đó, lấy một `correlation_id` có `latency_ms` cao.
  3. Mở trace cùng `correlation_id` trên Langfuse, so sánh các span chính để xác định bước nào bất thường.
- Mitigation tạm thời: dựa trên evidence thực tế để rollback prompt, khôi phục cấu hình liên quan, tắt practice scenario hoặc giảm tải khi demo.
- Owner: `student-2A202602756`

## Alert 1

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: tỷ lệ request hoàn tất trong 3 giây; mục tiêu 99.5% trong 28 ngày.
- Điều kiện và thời gian duy trì: P95 của `response_sent.latency_ms` lớn hơn 3000 ms liên tục 5 phút.
- Ảnh hưởng tới người dùng: người dùng phải chờ lâu hơn để nhận câu trả lời.
- Ba bước kiểm tra đầu tiên:
  1. **Metrics:** xác nhận P50/P95/P99 và TTFT trên dashboard, kiểm tra thời điểm bắt đầu và phạm vi ảnh hưởng.
  2. **Logs:** lọc `response_sent` trong `data/logs.jsonl`, lấy `correlation_id` và `latency_ms` cao.
  3. **Traces:** mở trace cùng `correlation_id` trên Langfuse, so sánh thời lượng `retrieval` và `generation`.
- Mitigation tạm thời: tắt scenario gây chậm hoặc giảm tải; nếu thời điểm tăng trùng thay đổi prompt thì rollback `production` về version đã biết tốt.
- Owner: `student-2A202602756`.

## Alert 2

- Tên: `ElevatedRequestFailures`
- Severity: `critical`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: tỷ lệ request thành công và retrieval success rate.
- Điều kiện và thời gian duy trì: error rate lớn hơn 2% hoặc retrieval success dưới 90% liên tục 5 phút.
- Ảnh hưởng tới người dùng: người dùng nhận lỗi thay vì câu trả lời hoặc câu trả lời thiếu dữ liệu liên quan.
- Ba bước kiểm tra đầu tiên:
  1. **Metrics:** xác nhận error rate, retrieval success và số request trong khoảng cảnh báo.
  2. **Logs:** lọc `request_failed` và các event có `tool_success=false`; ghi lại `error_type`, `session_id` và `correlation_id`.
  3. **Traces:** mở trace cùng `correlation_id`; kiểm tra span retrieval và lỗi/downstream span.
- Mitigation tạm thời: tắt scenario đang gây lỗi; khôi phục dịch vụ retrieval hoặc cấu hình truy cập đã biết tốt, sau đó xác nhận error rate giảm.
- Owner: `student-2A202602756`.

## Alert 3

- Tên: `QualityOrCostGuardrail`
- Severity: `warning`
- Duration: `10m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: quality proxy trung bình tối thiểu 0.75 và ngân sách chi phí 2.5 USD/ngày.
- Điều kiện và thời gian duy trì: quality trung bình dưới 0.75 hoặc chi phí ngày vượt 2.5 USD trong 10 phút.
- Ảnh hưởng tới người dùng: chất lượng câu trả lời suy giảm; tăng chi phí có thể làm vượt ngân sách vận hành.
- Ba bước kiểm tra đầu tiên:
  1. **Metrics:** xem quality, cost và token input/output theo cùng khoảng thời gian; kiểm tra số lượng mẫu.
  2. **Logs:** đối chiếu `quality_score`, `cost_usd`, `tokens_in`, `tokens_out`, `feature` và `correlation_id` ở các `response_sent`.
  3. **Traces:** mở trace tương ứng, xác nhận prompt version, model, usage và cost metadata.
- Mitigation tạm thời: rollback prompt nếu quality giảm sau thay đổi; giới hạn feature/request gây token tăng hoặc tạm tắt workload nếu ngân sách tiếp tục vượt.
- Owner: `student-2A202602756`.
