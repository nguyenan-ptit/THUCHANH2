# Thực hành Python AMQP — Bài 2 và Bài 3

## 1. Thông Tin Chung

| Họ và tên | Mã sinh viên |
| --- | --- |
| Nguyễn Văn An | B23DCCN004 |
| Đặng Kỳ Vĩ | B23DCCN914 |
| Vũ Thành Nguyên | B23DCCN617 |

| Môn học | Broker sử dụng |
| --- | --- |
| Internet of Things (IoT) | RabbitMQ (`localhost:5672`) |

## 2. Yêu Cầu Môi Trường

- Python 3.x.
- Thư viện `pika`.
- RabbitMQ đã cài đặt và đang chạy trên máy.

### Cài đặt thư viện

Trong môi trường Python muốn sử dụng, chạy:

```powershell
pip install pika
```

Các lệnh chạy chương trình bên dưới sử dụng `.venv`; cách tạo và cài thư viện vào môi trường này được trình bày ở mục **Chuẩn bị**.

### Khởi động RabbitMQ (nếu chưa chạy)

Trên máy thực hành, RabbitMQ được giải nén từ bản ZIP. Mở một terminal riêng tại thư mục dự án và chạy script khởi động có sẵn:

```powershell
Set-Location D:\TH
powershell -ExecutionPolicy Bypass -File .\start_rabbitmq.ps1
```

Script thiết lập đường dẫn Erlang và khởi động RabbitMQ đã có trên máy. Giữ terminal này mở, chờ `Starting broker... completed` rồi chạy các chương trình. Nếu broker đã chạy thì bỏ qua bước khởi động.

Lệnh `rabbitmq-service.bat start` chỉ dùng khi đã cài RabbitMQ dưới dạng Windows Service và thư mục `sbin` có trong PATH, hoặc khi gọi bằng đường dẫn đầy đủ. Xem [hướng dẫn Windows của RabbitMQ](https://www.rabbitmq.com/docs/install-windows-manual).

## 3. Cách chạy từng chương trình

### Chuẩn bị

Mở PowerShell tại thư mục dự án. Tạo `.venv` nếu chưa có, rồi cài thư viện:

```powershell
Set-Location D:\TH
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Với cấu hình RabbitMQ 4.3.6 đã dùng cho Bài 2, `%USERPROFILE%\rabbitmq\data\rabbitmq.conf` có dòng `deprecated_features.permit.transient_nonexcl_queues = true` để cho phép queue mặc định của bài.

Mỗi chương trình bên dưới chạy trong **một terminal riêng**, đều đặt `Set-Location D:\TH`. Chạy consumer trước, chờ thông báo `dang lang nghe`, rồi mới chạy producer.

### Bài 2 — Mô phỏng cảm biến IoT

| Thứ tự | Chương trình | Lệnh chạy |
| --- | --- | --- |
| 1 | Monitoring consumer | `.\.venv\Scripts\python.exe monitor_consumer_bai2.py` |
| 2 | Sensor producer | `.\.venv\Scripts\python.exe sensor_producer_bai2.py` |

Producer gửi JSON mỗi 3 giây và tiếp tục chạy đến khi dừng. Consumer nhận dữ liệu, in mã thiết bị, nhiệt độ, độ ẩm và cảnh báo.

### Bài 3 — Điều phối cảnh báo IoT

| Thứ tự | Chương trình | Lệnh chạy |
| --- | --- | --- |
| 1 | Warning consumer | `.\.venv\Scripts\python.exe -u warning_consumer_bai3.py` |
| 2 | Critical consumer | `.\.venv\Scripts\python.exe -u critical_consumer_bai3.py` |
| 3 | All alert consumer — tùy chọn | `.\.venv\Scripts\python.exe -u all_alert_consumer_bai3.py` |
| 4 | Alert producer | `.\.venv\Scripts\python.exe alert_producer_bai3.py` |

Producer gửi ba cảnh báo mẫu `info`, `warning`, `critical` rồi kết thúc. Các consumer tiếp tục lắng nghe. Có thể gửi thêm một cảnh báo tại terminal producer:

```powershell
.\.venv\Scripts\python.exe alert_producer_bai3.py warning "Nhiet do phong may vuot nguong"
```

Thay `warning` bằng `info` hoặc `critical` để gửi mức tương ứng. Dừng từng consumer và producer Bài 2 bằng **Ctrl+C**; dừng broker sau khi kết thúc thực hành.

## 4. Kết quả đạt được

Các kết quả tích hợp dưới đây được ghi nhận trong báo cáo và log chạy RabbitMQ ngày **17/10/2026**, với Python **3.14.0** và `pika` **1.4.4**.

### Bài 2

- Gửi/nhận thành công **5 message ngẫu nhiên** qua `sensor_data_queue`; consumer hiển thị đúng các giá trị producer gửi.
- JSON có đúng ba trường: `device_id` cố định là `"sensor01"`, `temperature` và `humidity` là số ngẫu nhiên. Producer nghỉ `sleep(3)` giữa các lần gửi.
- **7 trường hợp kiểm tra cảnh báo và giá trị biên đều đạt:** nhiệt độ `> 35` in `CANH BAO: Nhiet do cao`; độ ẩm `< 40` in `CANH BAO: Do am thap`. Khi cả hai điều kiện đúng, in cả hai cảnh báo theo thứ tự nhiệt độ rồi độ ẩm; bằng ngưỡng không gây cảnh báo tương ứng.
- Ctrl+C dừng được cả hai chương trình. Queue sau khi kết thúc có **0 message, 0 consumer**. Hai file đã kiểm tra cú pháp thành công.

### Bài 3

Với một lần producer gửi ba cảnh báo mẫu, các consumer nhận đúng:

| Consumer | Message nhận được |
| --- | --- |
| Warning consumer | 1 cảnh báo `warning` |
| Critical consumer | 1 cảnh báo `critical` |
| All alert consumer | 3 cảnh báo: `alert.info`, `alert.warning`, `alert.critical` |

Cảnh báo `info` trên direct exchange không tới warning consumer hoặc critical consumer. Consumer mở rộng nhận đủ ba mức qua topic exchange. Các consumer ghi kết quả vào `logs/warning_queue.log`, `logs/critical_queue.log` và `logs/all_alert_queue.log`.

Số lượng trên tính cho message mới của một lần chạy; queue và log có thể còn dữ liệu cũ. Khi đối chiếu, dùng thời gian của lần chạy hiện tại và chỉ mở một consumer cho mỗi queue.
