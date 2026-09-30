# Những việc còn lại trên Langfuse và ảnh evidence

## Trạng thái đã xác nhận

- Prompt tên `day13-chat` tồn tại trong project Langfuse đang cấu hình trên máy.
- Version 1 có labels `baseline` và `production`; version 2 có `candidate`.
- Đã chạy 10 trace baseline v1, 10 candidate v2, 10 production v2. Langfuse metadata xác nhận `prompt_source=langfuse` và đúng label/version.
- Đã promote `production` lên v2 rồi rollback về v1. API xác nhận trạng thái sau rollback: `baseline=1`, `production=1`, `candidate=2`.
- Batch workload đầu sau rollback gặp DNS lỗi. Sau khi kết nối phục hồi, đã gửi thêm một request: Langfuse xác nhận `production`, version 1, `prompt_source=langfuse`; trace `381a0be50c4f2d22b3bd10f71bea2e34`, correlation `req-4fcce137`.
- `.env` hiện đặt `LANGFUSE_PROMPT_NAME=day13-chat`, `LANGFUSE_PROMPT_LABEL=production`. Không chia sẻ/commit file hoặc key.

## Chụp ảnh Langfuse

Mở [Langfuse Cloud](https://cloud.langfuse.com), chọn đúng project cá nhân. Tên project phải nhìn thấy ở thanh điều hướng hoặc tiêu đề ảnh. **Không mở/chụp trang API Keys; không để secret/key trong ảnh.** Ảnh lưu trong `submission/evidence/`.

### `06-trace-list.png` — danh sách trace

1. Mở menu **Traces** trong project.
2. Chọn khoảng thời gian gần nhất và sắp xếp trace mới nhất trước.
3. Chụp trang thấy tên project và các trace gần nhất. Tối thiểu 10 traces đã được gửi cho candidate/production v2.

### `07-trace-waterfall.png` — cấu trúc và span chậm

1. Mở trace `8673ac582d602ab117129cd72eec65d6` (challenge baseline).
2. Mở rộng cây observations để thấy root `lab-agent-run`, child `retrieval`, child `generation`.
3. Chụp waterfall có tên span và thời lượng; retrieval là span bị chậm trong challenge.

### `08-trace-metadata.png` — correlation và prompt metadata

1. Trong cùng trace, chọn root `lab-agent-run` và mở phần metadata.
2. Đảm bảo thấy `correlation_id=req-24101db0`, `prompt_name=day13-chat`, `prompt_label=baseline`, `prompt_version=1`, `prompt_source=langfuse`.
3. Chọn generation để hiển thị model, token usage/cost nếu UI có chỗ riêng.
4. Không chụp input/output thô nếu UI đang hiện nội dung hội thoại.

### `09-prompt-versions.png` — hai prompt version

1. Mở **Prompt Management** hoặc **Prompts**, rồi chọn `day13-chat`.
2. Chụp bảng hiển thị version 1 (`baseline`, `production`) và version 2 (`candidate`). Ảnh cần thấy tên project/prompt và nhãn version.

### `10a-prompt-production-v2.png` — trạng thái sau promote

Label hiện đã rollback về version 1. Để có ảnh trạng thái promote, tạm thời chuyển label `production` sang version 2 trong trang `day13-chat`:

1. Mở phần versions/labels của `day13-chat`.
2. Ở version 2, gắn/chuyển label `production`; giữ `candidate` nếu UI cho phép.
3. Chụp bảng xác nhận version 2 đang mang `production`.

### `10b-prompt-production-v1.png` — trạng thái sau rollback

1. Chuyển label `production` từ version 2 về version 1.
2. Chụp bảng xác nhận version 1 mang `production` và version 2 còn `candidate`.
3. Để Langfuse ở trạng thái production=v1 sau khi chụp.

Label là con trỏ: chuyển `production` sang phiên bản cũ là rollback, không tạo version mới.

## Lệnh chạy lại trace sau rollback (chỉ khi cần trace mới)

Trace sau rollback đã được tạo. API local hiện đã dừng; `.env` đặt label `production`. Chỉ chạy các bước dưới đây nếu cần tạo thêm trace.

1. Mở PowerShell ở thư mục repo. Kiểm tra cổng 8000 còn trống; nếu đang được dùng, chọn cổng khác, ví dụ 8002.
2. Khởi động app:

   ```powershell
   .\.venv\Scripts\python.exe -m uvicorn app.main:app --env-file .env --host 127.0.0.1 --port 8000
   ```

3. Mở PowerShell thứ hai và kiểm tra:

   ```powershell
   Invoke-RestMethod http://127.0.0.1:8000/health
   ```

   Chỉ tiếp tục nếu `tracing_enabled` là `true` và `rag_slow` là `false`.

4. Tạo trace production sau rollback:

   ```powershell
   .\.venv\Scripts\python.exe scripts/load_test.py --concurrency 3 --base-url http://127.0.0.1:8000
   ```

5. Mở trace mới trong Langfuse. Chỉ tính nếu metadata ghi `prompt_source=langfuse`, `prompt_label=production`, `prompt_version=1`. Trace xác minh gần nhất đã đạt điều kiện; ID nằm trong `submission/evidence/10-production-v1-rollback-trace.txt`. Nếu chạy thêm lần nữa, kiểm tra tương tự.

## Chụp dashboard và challenge

### `11-dashboard-overview.png` — sáu panel

1. Mở PowerShell ở repo và chạy:

   ```powershell
   .\.venv\Scripts\python.exe scripts/dashboard.py
   ```

2. Mở `http://127.0.0.1:8501` trong browser.
3. Chụp ảnh toàn dashboard, thấy đủ sáu panel, khoảng thời gian, đơn vị, threshold/SLO và có dữ liệu. Nếu chữ nhỏ, dùng `11a`/`11b` để chia ảnh.

### `12-incident-metric.png` — metric challenge

Chụp dashboard có time range chứa `2026-09-30 05:40:20–05:40:33 UTC` (12:40:20–12:40:33 giờ Việt Nam). 5 request challenge có median latency 2,654 ms, vượt ngưỡng 2,000 ms. Số liệu text nằm trong `12-incident-metric.json` và `13-incident-load.txt`.

### `13-incident-log.png` — log nối correlation ID

Mở `submission/evidence/13-incident-log.txt` trong editor, chụp phần `response_sent` với một correlation ID, feature `monitoring`, `tool_name=retrieval` và latency. Log text đã được lọc, không chứa message thô.

### `14-incident-trace.png` — trace cùng correlation ID

Mở lại trace `8673ac582d602ab117129cd72eec65d6`, correlation `req-24101db0`, rồi chụp root/retrieval/generation và thời lượng span. Đây là trace của request challenge đại diện cùng log ở trên.

## Cập nhật report sau khi lưu ảnh

Trong `submission/REPORT.md`, tên project và trace ID `production` v1 đã điền. Lưu ảnh vào evidence index, rồi điền commit SHA sau commit cuối. Không đánh dấu checklist cuối cho đến khi ảnh thực sự tồn tại trong `submission/evidence/`.
