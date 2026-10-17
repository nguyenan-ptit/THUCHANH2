# Thực hành Python AMQP — Bài 2 và Bài 3

**Sinh viên:** Vũ Thành Nguyên — **Mã sinh viên:** B23DCCN617.

Các chương trình và `requirements.txt` được đặt trực tiếp trong thư mục `D:\TH`. Dự án dùng Python 3.x và thư viện `pika`.

## 1. Broker sử dụng

| Thiết lập | Giá trị |
| --- | --- |
| Broker trong các lần chạy đã ghi nhận | RabbitMQ 4.3.6, AMQP 0-9-1, Erlang/OTP 28.5 |
| Host | `localhost` |
| Cổng AMQP | `5672` |
| Virtual host | `/` |
| Tài khoản cục bộ | `guest` / `guest` |
| Bài 2 | Queue `sensor_data_queue`, default exchange `""`, routing key `sensor_data_queue` |
| Bài 3 | Direct exchange `iot_alert_exchange`; `warning_queue` nhận key `warning`, `critical_queue` nhận key `critical` |
| Bài 3 mở rộng hiện có | Topic exchange `iot_alert_topic_exchange`; `all_alert_queue` nhận key `alert.#` |

RabbitMQ là dịch vụ riêng; cài `pika` không cài RabbitMQ. Nếu broker đã chạy, chuyển sang bước chạy chương trình.

Trên máy thực hành, RabbitMQ và Erlang đã được giải nén trong `%USERPROFILE%\rabbitmq`, với hai thư mục `rabbitmq_server-4.3.6` và `otp28`. Mở một terminal tại `D:\TH` để khởi động:

```powershell
Set-Location D:\TH
powershell -ExecutionPolicy Bypass -File .\start_rabbitmq.ps1
```

Script chỉ khởi động broker đã có trên máy. Giữ terminal này mở và chờ dòng `Starting broker... completed` trước khi chạy các chương trình.

Theo cấu hình đã ghi nhận, broker trên máy thực hành dùng dòng sau trong `%USERPROFILE%\rabbitmq\data\rabbitmq.conf` để cho phép queue với thuộc tính mặc định của Bài 2:

```ini
deprecated_features.permit.transient_nonexcl_queues = true
```

Nếu thay đổi cấu hình broker thì cần khởi động lại dịch vụ. Hai chương trình Bài 2 cùng khai báo `queue_declare(queue="sensor_data_queue")` với thuộc tính mặc định.

Nếu dùng broker của lớp:

- **Bài 2:** sửa các hằng số `HOST`, `PORT`, `VIRTUAL_HOST`, `USERNAME`, `PASSWORD` ở đầu cả hai file cho giống nhau.
- **Bài 3:** đặt các biến môi trường `RABBITMQ_HOST`, `RABBITMQ_PORT`, `RABBITMQ_USER`, `RABBITMQ_PASS` trong từng terminal; các script hiện dùng vhost `/`.

Dùng tài khoản được cấp khi kết nối từ xa; không dùng `guest` và không ghi mật khẩu broker dùng chung vào báo cáo.

## 2. Cách chạy từng chương trình

### Chuẩn bị môi trường Python

Mở PowerShell tại thư mục dự án. Nếu chưa có môi trường `.venv`, tạo môi trường rồi cài thư viện:

```powershell
Set-Location D:\TH
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Nếu đã có `.venv` dùng được thì bỏ qua lệnh tạo môi trường. Nếu `python` chưa có trong PATH, có thể dùng `py -3 -m venv .venv` khi đã cài Python Launcher. `requirements.txt` chỉ khai báo thư viện ngoài `pika`.

### Bài 2 — Mô phỏng cảm biến IoT

Mở hai terminal tại `D:\TH`, chạy consumer trước producer và dùng cùng môi trường Python.

**Terminal 1 — `monitor_consumer_bai2.py`:** nhận JSON, in mã thiết bị, nhiệt độ, độ ẩm và cảnh báo.

```powershell
.\.venv\Scripts\python.exe monitor_consumer_bai2.py
```

**Terminal 2 — `sensor_producer_bai2.py`:** sinh dữ liệu cảm biến và gửi một message mỗi 3 giây.

```powershell
.\.venv\Scripts\python.exe sensor_producer_bai2.py
```

Mỗi message có đúng ba trường `device_id`, `temperature`, `humidity`. `device_id` luôn là `"sensor01"`; nhiệt độ được sinh ngẫu nhiên trong khoảng 20–40, độ ẩm trong khoảng 30–80, làm tròn một chữ số thập phân. Đây là khoảng chọn để thực hành. Producer in payload đã gửi; consumer giải mã UTF-8 và phân tích JSON để in cùng các giá trị.

### Bài 3 — Điều phối cảnh báo IoT

Trước tiên cài thư viện theo mục **Chuẩn bị môi trường Python** ở trên. Dùng PowerShell và Python trong `.venv` cho tất cả lệnh dưới đây.

Bài 3 cơ bản dùng **4 terminal**: broker, warning consumer, critical consumer và producer. Nếu chạy thêm all alert consumer thì dùng **5 terminal**. Các bước bên dưới có cả phần mở rộng; có thể bỏ qua Terminal 4 khi chỉ chạy bài cơ bản. Nếu broker đã chạy, giữ broker đó và bỏ qua Terminal 1.

**Terminal 1 — Khởi động RabbitMQ trên máy thực hành**

```powershell
Set-Location D:\TH
powershell -ExecutionPolicy Bypass -File .\start_rabbitmq.ps1
```

Giữ terminal này mở. Chờ dòng `Starting broker... completed` rồi tiếp tục. Script yêu cầu RabbitMQ/Erlang đã được chuẩn bị như mục **Broker sử dụng**.

**Terminal 2 — Chạy warning consumer**

```powershell
Set-Location D:\TH
.\.venv\Scripts\python.exe -u warning_consumer_bai3.py
```

Chờ dòng thông báo:

```text
[*] warning_queue dang lang nghe iot_alert_exchange (routing key='warning'). Nhan Ctrl+C de dung.
```

Consumer này nhận cảnh báo có routing key `warning`.

**Terminal 3 — Chạy critical consumer**

```powershell
Set-Location D:\TH
.\.venv\Scripts\python.exe -u critical_consumer_bai3.py
```

Chờ dòng thông báo:

```text
[*] critical_queue dang lang nghe iot_alert_exchange (routing key='critical'). Nhan Ctrl+C de dung.
```

Consumer này nhận cảnh báo có routing key `critical`.

**Terminal 4 — Chạy all alert consumer (tùy chọn, phần mở rộng)**

```powershell
Set-Location D:\TH
.\.venv\Scripts\python.exe -u all_alert_consumer_bai3.py
```

Chờ dòng thông báo:

```text
[*] all_alert_queue dang lang nghe iot_alert_topic_exchange (pattern='alert.#'). Nhan Ctrl+C de dung.
```

Consumer này nhận cả `info`, `warning`, `critical` qua topic exchange.

**Terminal 5 — Chạy producer sau khi các consumer đã sẵn sàng**

```powershell
Set-Location D:\TH
.\.venv\Scripts\python.exe alert_producer_bai3.py
```

Producer gửi **3 cảnh báo mẫu** gồm `info`, `warning`, `critical`, in các dòng `Da gui` rồi kết thúc. Các consumer tiếp tục lắng nghe. Chạy consumer trước producer để queue được tạo và bind; ở lần chạy đầu, gửi khi chưa có queue được bind có thể làm mất message.

Với một lần chạy producer mặc định, số **message mới** mong đợi là:

| Consumer | Message mới nhận được |
| --- | --- |
| Warning consumer | 1 cảnh báo `warning` |
| Critical consumer | 1 cảnh báo `critical` |
| All alert consumer, nếu đã bật | 3 cảnh báo: `alert.info`, `alert.warning`, `alert.critical` |

Bản `info` gửi vào direct exchange không tới warning consumer hoặc critical consumer.

**Gửi thêm một cảnh báo tùy chọn tại terminal producer**

Mỗi lệnh sau gửi một cảnh báo; đặt nội dung trong dấu ngoặc kép nếu có khoảng trắng:

```powershell
.\.venv\Scripts\python.exe alert_producer_bai3.py warning "Nhiet do phong may vuot nguong warning"
.\.venv\Scripts\python.exe alert_producer_bai3.py critical "Mat dien rack so 3 critical"
.\.venv\Scripts\python.exe alert_producer_bai3.py info "Thiet bi sensor02 khoi dong lai info"
```

Nếu chạy cả ba lệnh này sau producer mặc định, tổng số message mới là **2 warning, 2 critical và 6 ở all alert consumer** nếu đã bật consumer mở rộng.

**Đối chiếu kết quả và dừng chương trình**

Các consumer ghi nối vào `logs/warning_queue.log`, `logs/critical_queue.log` và `logs/all_alert_queue.log`. Đối chiếu các dòng có thời gian của lần chạy hiện tại. Queue có thể còn message từ lần trước nên tổng số dòng hiển thị có thể lớn hơn số message mới trong bảng. Chỉ chạy một consumer cho mỗi queue khi đối chiếu.

Nhấn **Ctrl+C** tại từng terminal consumer để dừng. Nếu đã khởi động broker ở Terminal 1, dừng broker sau khi kết thúc các chương trình.

Dừng từng chương trình bằng **Ctrl+C**. Trên Linux/macOS, dùng `.venv/bin/python` thay cho `.\.venv\Scripts\python.exe`.

## 3. Kết quả đạt được

### Bài 2 — Kết quả chạy đã ghi nhận ngày 17/10/2026

Theo báo cáo kiểm tra đã lưu trước khi di chuyển file, môi trường chạy là Python **3.14.0**, `pika` **1.4.4**, RabbitMQ **4.3.6** tại `localhost:5672`, vhost `/`.

- Đã gửi/nhận thành công **5 message ngẫu nhiên qua RabbitMQ**. Mỗi JSON có đúng ba trường; consumer in đúng mã thiết bị và hai giá trị cảm biến do producer gửi.
- Producer dùng `time.sleep(3)` giữa các lần gửi; lần kiểm tra không đo độ chính xác thời gian thực.
- Đã gửi **7 payload kiểm tra qua cùng queue** để xác minh các cảnh báo và giá trị biên trong bảng dưới.
- Đã dừng cả hai chương trình bằng Ctrl+C. Sau khi kết thúc, `sensor_data_queue` có **0 message, 0 consumer**.

Các cặp `(temperature, humidity)` đã đối chiếu: `(26.6, 60.2)`, `(29.3, 49.9)`, `(23.9, 50.3)`, `(31.4, 61.8)`, `(27.7, 67.8)`. Những lần chạy sau sẽ sinh giá trị khác.

| Nhiệt độ | Độ ẩm | Cảnh báo đã ghi nhận |
| --- | --- | --- |
| 29.5 | 62.1 | Không có |
| 36.4 | 62.1 | `CANH BAO: Nhiet do cao` |
| 29.5 | 38.9 | `CANH BAO: Do am thap` |
| 36.4 | 38.9 | `CANH BAO: Nhiet do cao`, sau đó `CANH BAO: Do am thap` |
| 35.0 | 40.0 | Không có |
| 35.1 | 40.0 | `CANH BAO: Nhiet do cao` |
| 35.0 | 39.9 | `CANH BAO: Do am thap` |

Ví dụ đầu ra consumer với payload có cả hai điều kiện cảnh báo:

```text
Device: sensor01
Temperature: 36.4
Humidity: 38.9
CANH BAO: Nhiet do cao
CANH BAO: Do am thap
```

Hai điều kiện được kiểm tra bằng hai `if` độc lập: `temperature > 35` và `humidity < 40`. Giá trị bằng `35` hoặc `40` không gây cảnh báo tương ứng.

### Bài 3 — Kết quả theo nhật ký kiểm tra đã lưu

| Kịch bản | Warning consumer | Critical consumer | All alert consumer |
| --- | --- | --- | --- |
| Ngày 17/10/2026: producer gửi ba cảnh báo mẫu | 1 message | 1 message | 3 message |
| Ngày 15/10/2026: ba cảnh báo mẫu, thêm một `critical` và một `info` | 1 message | 2 message | 5 message |

Các log đã lưu ghi nhận cảnh báo được phân phối đúng routing key: `warning` tới `warning_queue`, `critical` tới `critical_queue`; bản `info` trên direct exchange không tới hai queue này. All alert consumer nhận đủ cả ba mức qua topic exchange. Báo cáo trước đó ghi nhận ba queue Bài 3 còn **0 message** sau khi xử lý.

### Kiểm tra sau khi di chuyển file

- `sensor_producer_bai2.py`, `monitor_consumer_bai2.py` và `requirements.txt` đã được chuyển ra `D:\TH`; nội dung được đối chiếu bằng SHA-256 và giữ nguyên.
- Đã kiểm tra cú pháp hai chương trình tại đường dẫn mới bằng:

```powershell
.\.venv\Scripts\python.exe -m py_compile sensor_producer_bai2.py monitor_consumer_bai2.py
```

Kết quả: không có lỗi cú pháp. Lần chỉnh sửa này không chạy lại kết nối hoặc giao nhận RabbitMQ; các kết quả tích hợp ở trên được giữ từ báo cáo và nhật ký trước đó.
