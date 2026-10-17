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

### Terminal 1 — Khởi động RabbitMQ (nếu chưa chạy)

Trên máy thực hành, RabbitMQ được giải nén từ bản ZIP. Mở một terminal riêng tại thư mục dự án và chạy script khởi động có sẵn:

```powershell
Set-Location D:\TH
powershell -ExecutionPolicy Bypass -File .\start_rabbitmq.ps1
```

Script thiết lập đường dẫn Erlang và khởi động RabbitMQ đã có trên máy. Giữ **Terminal 1** mở trong suốt quá trình chạy cả hai bài, chờ `Starting broker... completed` rồi tiếp tục. Nếu broker đã chạy thì bỏ qua bước khởi động.

Lệnh `rabbitmq-service.bat start` chỉ dùng khi đã cài RabbitMQ dưới dạng Windows Service và thư mục `sbin` có trong PATH, hoặc khi gọi bằng đường dẫn đầy đủ. Xem [hướng dẫn Windows của RabbitMQ](https://www.rabbitmq.com/docs/install-windows-manual).

## 3. Cách chạy từng chương trình

Mỗi terminal là một cửa sổ hoặc tab **PowerShell riêng**. Mọi terminal đều làm việc tại `D:\TH` và dùng cùng Python trong `.venv`. Chạy lần lượt từng bài; khi chuyển từ Bài 2 sang Bài 3, dừng các chương trình Bài 2 bằng Ctrl+C và giữ Terminal 1 chạy broker.

### Chuẩn bị môi trường — thực hiện một lần tại Terminal 2

Tạo `.venv` nếu chưa có, rồi cài thư viện:

```powershell
Set-Location D:\TH
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Nếu đã có `.venv`, bỏ qua lệnh tạo môi trường. Với cấu hình RabbitMQ 4.3.6 đã dùng cho Bài 2, `%USERPROFILE%\rabbitmq\data\rabbitmq.conf` có dòng `deprecated_features.permit.transient_nonexcl_queues = true` để cho phép queue mặc định của bài.

### Bài 2 — Mô phỏng cảm biến IoT

Giữ **Terminal 1** chạy broker. Dùng **Terminal 2** cho consumer và **Terminal 3** cho producer.

**Terminal 2 — Chạy Monitoring Consumer trước**

```powershell
Set-Location D:\TH
.\.venv\Scripts\python.exe -u monitor_consumer_bai2.py
```

Chờ dòng `Monitoring consumer dang lang nghe. Nhan Ctrl+C de dung.` rồi mở terminal tiếp theo.

**Terminal 3 — Chạy Sensor Producer**

```powershell
Set-Location D:\TH
.\.venv\Scripts\python.exe -u sensor_producer_bai2.py
```

Producer gửi JSON mỗi 3 giây và in `Da gui`. Consumer ở Terminal 2 hiển thị dữ liệu và cảnh báo tương ứng. Cả hai tiếp tục chạy đến khi nhấn **Ctrl+C** tại từng terminal.

### Bài 3 — Điều phối cảnh báo IoT

Giữ **Terminal 1** chạy broker. Mở riêng các terminal dưới đây theo thứ tự. **Terminal 4 là phần mở rộng tùy chọn**; có thể bỏ qua nếu chỉ chạy bài cơ bản.

**Terminal 2 — Chạy Warning Consumer**

```powershell
Set-Location D:\TH
.\.venv\Scripts\python.exe -u warning_consumer_bai3.py
```

Chờ thông báo `warning_queue dang lang nghe`.

**Terminal 3 — Chạy Critical Consumer**

```powershell
Set-Location D:\TH
.\.venv\Scripts\python.exe -u critical_consumer_bai3.py
```

Chờ thông báo `critical_queue dang lang nghe`.

**Terminal 4 — Chạy All Alert Consumer (tùy chọn)**

```powershell
Set-Location D:\TH
.\.venv\Scripts\python.exe -u all_alert_consumer_bai3.py
```

Chờ thông báo `all_alert_queue dang lang nghe`. Consumer này nhận đủ ba mức cảnh báo qua topic exchange.

**Terminal 5 — Chạy Alert Producer sau khi các consumer đã sẵn sàng**

```powershell
Set-Location D:\TH
.\.venv\Scripts\python.exe -u alert_producer_bai3.py
```

Producer gửi ba cảnh báo mẫu `info`, `warning`, `critical` rồi kết thúc. Các consumer tiếp tục lắng nghe. Muốn gửi thêm một cảnh báo, chạy tại **Terminal 5**:

```powershell
.\.venv\Scripts\python.exe -u alert_producer_bai3.py warning "Nhiet do phong may vuot nguong"
```

Thay `warning` bằng `info` hoặc `critical` để gửi mức tương ứng. Nhấn **Ctrl+C** tại từng terminal consumer để dừng. Dừng broker ở Terminal 1 sau khi kết thúc thực hành.

## 4. Kết quả đạt được

Các kết quả tích hợp được ghi nhận trong báo cáo và log RabbitMQ ngày **17/10/2026**, với Python **3.14.0** và `pika` **1.4.4**. Các khối terminal dưới đây trình bày lại dữ liệu đã ghi nhận theo định dạng in của mã nguồn; đây không phải phiên chạy mới. Thời gian và giá trị ngẫu nhiên sẽ thay đổi khi chạy lại.

### Bài 2 — Đầu ra ở Terminal 3 (Producer)

Đã gửi/nhận thành công 5 message ngẫu nhiên. Dưới đây là phần trích hai message trong báo cáo đã lưu:

```text
PS D:\TH> .\.venv\Scripts\python.exe -u sensor_producer_bai2.py
Sensor producer dang chay. Nhan Ctrl+C de dung.
Da gui: {"device_id": "sensor01", "temperature": 26.6, "humidity": 60.2}
Da gui: {"device_id": "sensor01", "temperature": 29.3, "humidity": 49.9}
```

### Bài 2 — Đầu ra tương ứng ở Terminal 2 (Consumer)

```text
PS D:\TH> .\.venv\Scripts\python.exe -u monitor_consumer_bai2.py
Monitoring consumer dang lang nghe. Nhan Ctrl+C de dung.
Device: sensor01
Temperature: 26.6
Humidity: 60.2

Device: sensor01
Temperature: 29.3
Humidity: 49.9
```

Cả 7 trường hợp kiểm tra cảnh báo và giá trị biên đã đạt. Khi gửi payload kiểm tra có nhiệt độ `36.4`, độ ẩm `38.9` vào cùng queue, Terminal 2 in cả hai cảnh báo:

```text
Device: sensor01
Temperature: 36.4
Humidity: 38.9
CANH BAO: Nhiet do cao
CANH BAO: Do am thap
```

Với giá trị biên `35.0` và `40.0`, Terminal 2 chỉ in dữ liệu:

```text
Device: sensor01
Temperature: 35.0
Humidity: 40.0
```

Đã kiểm tra Ctrl+C dừng được cả hai chương trình; queue sau khi kết thúc có **0 message, 0 consumer**. Hai file Bài 2 đã kiểm tra cú pháp thành công.

### Bài 3 — Đầu ra mong đợi ở Terminal 5 (Producer)

Producer không lưu console vào file log. Với ba cảnh báo mẫu trong mã nguồn, đầu ra là:

```text
PS D:\TH> .\.venv\Scripts\python.exe -u alert_producer_bai3.py
[x] Da gui [info] -> iot_alert_exchange: Cam bien phong may 1 gui du lieu binh thuong info
[x] Da gui [warning] -> iot_alert_exchange: Nhiet do phong may vuot nguong warning
[x] Da gui [critical] -> iot_alert_exchange: Cam bien kho lanh mat ket noi critical
PS D:\TH>
```

Các đầu ra consumer dưới đây được dựng lại từ log của lần gửi ba cảnh báo mẫu lúc **14:54:34 ngày 17/10/2026**.

### Bài 3 — Đầu ra ở Terminal 2 (Warning Consumer)

```text
PS D:\TH> .\.venv\Scripts\python.exe -u warning_consumer_bai3.py
[*] warning_queue dang lang nghe iot_alert_exchange (routing key='warning'). Nhan Ctrl+C de dung.
[warning_queue] Da nhan: Nhiet do phong may vuot nguong warning | gui boi Vu Thanh Nguyen - B23DCCN617 | 14:54:34
    routing key: warning | thoi gian nhan: 2026-10-17 14:54:34
```

### Bài 3 — Đầu ra ở Terminal 3 (Critical Consumer)

```text
PS D:\TH> .\.venv\Scripts\python.exe -u critical_consumer_bai3.py
[*] critical_queue dang lang nghe iot_alert_exchange (routing key='critical'). Nhan Ctrl+C de dung.
[critical_queue] Da nhan: Cam bien kho lanh mat ket noi critical | gui boi Vu Thanh Nguyen - B23DCCN617 | 14:54:34
    routing key: critical | thoi gian nhan: 2026-10-17 14:54:34
    !!! CANH BAO NGHIEM TRONG - CAN XU LY NGAY !!!
```

### Bài 3 — Đầu ra ở Terminal 4 (All Alert Consumer, nếu đã bật)

```text
PS D:\TH> .\.venv\Scripts\python.exe -u all_alert_consumer_bai3.py
[*] all_alert_queue dang lang nghe iot_alert_topic_exchange (pattern='alert.#'). Nhan Ctrl+C de dung.
[all_alert_queue] Da nhan (alert.info): Cam bien phong may 1 gui du lieu binh thuong info | gui boi Vu Thanh Nguyen - B23DCCN617 | 14:54:34
[all_alert_queue] Da nhan (alert.warning): Nhiet do phong may vuot nguong warning | gui boi Vu Thanh Nguyen - B23DCCN617 | 14:54:34
[all_alert_queue] Da nhan (alert.critical): Cam bien kho lanh mat ket noi critical | gui boi Vu Thanh Nguyen - B23DCCN617 | 14:54:34
```

Lần chạy này ghi nhận Warning Consumer nhận **1** message, Critical Consumer nhận **1** message, All Alert Consumer nhận **3** message. Bản `info` trên direct exchange không tới hai queue warning/critical.

Các log được lưu tại `logs/warning_queue.log`, `logs/critical_queue.log` và `logs/all_alert_queue.log`. Số lượng trên tính cho message mới của một lần chạy; khi đối chiếu, dùng thời gian của lần chạy hiện tại và chỉ mở một consumer cho mỗi queue vì queue/log có thể còn dữ liệu cũ.
