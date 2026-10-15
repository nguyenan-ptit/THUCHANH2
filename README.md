# Bài 3: Mô phỏng hệ thống điều phối cảnh báo IoT với exchange (AMQP)

| | |
|---|---|
| **Sinh viên** | Vũ Thành Nguyên |
| **Mã sinh viên** | B23DCCN617 |
| **Ngôn ngữ / thư viện** | Python 3.14, `pika` 1.4.4 |
| **Broker** | RabbitMQ 4.3.6 (AMQP 0-9-1) chạy trên Erlang/OTP 28 |

## 1. Mục tiêu

Làm quen với **exchange** và **routing key** trong AMQP. Producer gửi cảnh báo IoT với 3 mức `info`, `warning`, `critical` vào một direct exchange. Mỗi consumer chỉ nhận đúng mức cảnh báo mà queue của nó được bind.

## 2. Danh sách file nộp

| File | Vai trò |
|---|---|
| `alert_producer_bai3.py` | **Chương trình 1 (Alert Producer).** Tạo direct exchange `iot_alert_exchange`, gửi cảnh báo với routing key `info` / `warning` / `critical` |
| `warning_consumer_bai3.py` | **Chương trình 2 (Warning Consumer).** Tạo `warning_queue`, bind với routing key `warning` |
| `critical_consumer_bai3.py` | **Chương trình 3 (Critical Consumer).** Tạo `critical_queue`, bind với routing key `critical` |
| `all_alert_consumer_bai3.py` | **Mở rộng 1.** Consumer nhận *tất cả* cảnh báo qua topic exchange `iot_alert_topic_exchange` |
| `logs/*.log` | **Mở rộng 2.** File log cảnh báo do các consumer ghi ra |
| `start_rabbitmq.ps1` | Script khởi động broker RabbitMQ trên máy |
| `README.md` | Tài liệu này |

## 3. Broker sử dụng

- **RabbitMQ 4.3.6**, cổng AMQP `5672`, vhost `/`, tài khoản mặc định `guest` / `guest` (chỉ đăng nhập được từ localhost).
- Trên máy thực hành, broker chạy từ bản zip chính thức (không cần quyền admin), đặt trong `%USERPROFILE%\rabbitmq`:
  - `rabbitmq_server-4.3.6\`: RabbitMQ server
  - `otp28\`: Erlang/OTP 28.5. Lưu ý: RabbitMQ 4.3 **không** chạy được với Erlang OTP 29, sẽ báo lỗi `incompatible_feature_flags`.
  - `data\`: dữ liệu và log của broker

### Khởi động broker

```powershell
powershell -ExecutionPolicy Bypass -File .\start_rabbitmq.ps1
```

Để cửa sổ này mở trong suốt quá trình chạy bài. Khi thấy dòng `Starting broker... completed` là broker đã sẵn sàng.

Cách khác: dùng Docker (`docker run -d -p 5672:5672 -p 15672:15672 rabbitmq:3-management`) hoặc broker dùng chung của lớp.

### Đổi broker (không cần sửa code)

Mọi chương trình đọc cấu hình kết nối từ biến môi trường:

| Biến | Mặc định |
|---|---|
| `RABBITMQ_HOST` | `localhost` |
| `RABBITMQ_PORT` | `5672` |
| `RABBITMQ_USER` | `guest` |
| `RABBITMQ_PASS` | `guest` |

Ví dụ với broker của lớp (PowerShell, đặt trong **từng** terminal):

```powershell
$env:RABBITMQ_HOST="192.168.1.10"; $env:RABBITMQ_USER="sv"; $env:RABBITMQ_PASS="matkhau"
```

## 4. Thiết kế

### Sơ đồ định tuyến

```
                                    routing key
                                 ┌── "warning"  ──► warning_queue  ──► warning_consumer_bai3.py
Producer ──► iot_alert_exchange ─┼── "critical" ──► critical_queue ──► critical_consumer_bai3.py
             (direct)            └── "info"     ──► (không queue nào bind → message bị bỏ)

             (mở rộng)              binding key
Producer ──► iot_alert_topic_exchange ── "alert.#" ──► all_alert_queue ──► all_alert_consumer_bai3.py
             (topic, routing key = alert.info | alert.warning | alert.critical)
```

### Thành phần AMQP

| Thành phần | Tên | Kiểu / thuộc tính |
|---|---|---|
| Exchange | `iot_alert_exchange` | `direct`, durable |
| Exchange (mở rộng) | `iot_alert_topic_exchange` | `topic`, durable |
| Queue | `warning_queue` | durable, bind `iot_alert_exchange` với key `warning` |
| Queue | `critical_queue` | durable, bind `iot_alert_exchange` với key `critical` |
| Queue (mở rộng) | `all_alert_queue` | durable, bind `iot_alert_topic_exchange` với key `alert.#` |

### Chi tiết xử lý

- **Producer**: khai báo cả 2 exchange. Mỗi cảnh báo được publish 2 lần: vào direct exchange với key `<mức>` và vào topic exchange với key `alert.<mức>`. Message ở dạng persistent (`delivery_mode=2`). Nội dung có kèm tên, mã sinh viên và giờ gửi. Mức cảnh báo được kiểm tra, mức không hợp lệ sẽ bị từ chối.
- **Consumer**: khai báo lại exchange và queue (thao tác idempotent nên không phụ thuộc thứ tự khởi động), rồi bind đúng key. Consumer dùng `basic_qos(prefetch_count=1)` và **ack thủ công** sau khi xử lý xong, nên message không bị mất nếu consumer chết giữa chừng. Mỗi message nhận được sẽ in ra màn hình kèm routing key và thời gian nhận, đồng thời ghi vào file log. Dừng consumer bằng `Ctrl+C`.
- **Ghi log**: mỗi consumer ghi vào một file riêng, `logs/<tên_queue>.log`. Lý do: khi thử cho 3 tiến trình cùng ghi nối vào một file chung trên Windows thì bị mất dòng, vì các lần ghi đè lên nhau.

## 5. Cách chạy

### Cài thư viện

```bash
pip install pika
```

### Chạy

Mở **5 terminal**, các terminal 2 đến 5 đều `cd` tới thư mục bài làm. Chạy **consumer trước producer**. Nếu producer chạy khi chưa có queue nào được bind, exchange không có nơi chuyển message và message sẽ bị bỏ.

| Terminal | Lệnh | Ghi chú |
|---|---|---|
| 1 | `powershell -ExecutionPolicy Bypass -File .\start_rabbitmq.ps1` | Broker (bỏ qua nếu dùng broker khác) |
| 2 | `python warning_consumer_bai3.py` | |
| 3 | `python critical_consumer_bai3.py` | |
| 4 | `python all_alert_consumer_bai3.py` | Mở rộng |
| 5 | `python alert_producer_bai3.py` | Gửi 3 cảnh báo mẫu |

Gửi một cảnh báo tùy chọn:

```bash
python alert_producer_bai3.py warning "Nhiet do phong may chuot muc warning"
python alert_producer_bai3.py critical "Mat dien rack so 3 critical"
python alert_producer_bai3.py info "Thiet bi sensor02 khoi dong lai info"
```

Sau lần chạy đầu, các queue đã được tạo (durable). Vì vậy nếu sau đó producer gửi khi consumer đang tắt, message vẫn nằm chờ trong queue và consumer sẽ nhận khi bật lại.

## 6. Kết quả đạt được (chạy thật ngày 15/10/2026)

Kịch bản: bật 3 consumer, chạy producer với 3 cảnh báo mẫu, sau đó gửi thêm 1 cảnh báo `critical` và 1 cảnh báo `info` tùy chọn.

**Producer**

```
[x] Da gui [info] -> iot_alert_exchange: Cam bien phong may 1 gui du lieu binh thuong info
[x] Da gui [warning] -> iot_alert_exchange: Nhiet do phong may vuot nguong warning
[x] Da gui [critical] -> iot_alert_exchange: Cam bien kho lanh mat ket noi critical
[x] Da gui [critical] -> iot_alert_exchange: Mat dien rack so 3 critical
[x] Da gui [info] -> iot_alert_exchange: Thiet bi sensor02 khoi dong lai info
```

**Warning consumer**: chỉ nhận cảnh báo `warning`

```
[*] warning_queue dang lang nghe iot_alert_exchange (routing key='warning'). Nhan Ctrl+C de dung.
[warning_queue] Da nhan: Nhiet do phong may vuot nguong warning | gui boi Vu Thanh Nguyen - B23DCCN617 | 13:48:59
    routing key: warning | thoi gian nhan: 2026-10-15 13:48:59
```

**Critical consumer**: chỉ nhận cảnh báo `critical`

```
[*] critical_queue dang lang nghe iot_alert_exchange (routing key='critical'). Nhan Ctrl+C de dung.
[critical_queue] Da nhan: Cam bien kho lanh mat ket noi critical | gui boi Vu Thanh Nguyen - B23DCCN617 | 13:48:59
    routing key: critical | thoi gian nhan: 2026-10-15 13:48:59
    !!! CANH BAO NGHIEM TRONG - CAN XU LY NGAY !!!
[critical_queue] Da nhan: Mat dien rack so 3 critical | gui boi Vu Thanh Nguyen - B23DCCN617 | 13:48:59
    routing key: critical | thoi gian nhan: 2026-10-15 13:48:59
    !!! CANH BAO NGHIEM TRONG - CAN XU LY NGAY !!!
```

**Cảnh báo `info`**: không xuất hiện ở warning consumer hay critical consumer, đúng như yêu cầu.

**All alert consumer (mở rộng, topic exchange)**: nhận đủ cả 3 mức

```
[*] all_alert_queue dang lang nghe iot_alert_topic_exchange (pattern='alert.#'). Nhan Ctrl+C de dung.
[all_alert_queue] Da nhan (alert.info): Cam bien phong may 1 gui du lieu binh thuong info | gui boi Vu Thanh Nguyen - B23DCCN617 | 13:48:59
[all_alert_queue] Da nhan (alert.warning): Nhiet do phong may vuot nguong warning | gui boi Vu Thanh Nguyen - B23DCCN617 | 13:48:59
[all_alert_queue] Da nhan (alert.critical): Cam bien kho lanh mat ket noi critical | gui boi Vu Thanh Nguyen - B23DCCN617 | 13:48:59
[all_alert_queue] Da nhan (alert.critical): Mat dien rack so 3 critical | gui boi Vu Thanh Nguyen - B23DCCN617 | 13:48:59
[all_alert_queue] Da nhan (alert.info): Thiet bi sensor02 khoi dong lai info | gui boi Vu Thanh Nguyen - B23DCCN617 | 13:49:01
```

**File log (mở rộng)**, ví dụ `logs/critical_queue.log`:

```
2026-10-15 13:48:59 [critical_queue] [critical] Cam bien kho lanh mat ket noi critical | gui boi Vu Thanh Nguyen - B23DCCN617 | 13:48:59
2026-10-15 13:48:59 [critical_queue] [critical] Mat dien rack so 3 critical | gui boi Vu Thanh Nguyen - B23DCCN617 | 13:48:59
```

**Kiểm tra trên broker** bằng `rabbitmqctl`:

```
> rabbitmqctl list_exchanges name type
iot_alert_exchange        direct
iot_alert_topic_exchange  topic

> rabbitmqctl list_bindings source_name destination_name routing_key
iot_alert_topic_exchange  all_alert_queue  alert.#
iot_alert_exchange        warning_queue    warning
iot_alert_exchange        critical_queue   critical

> rabbitmqctl list_queues name messages
critical_queue   0
all_alert_queue  0
warning_queue    0
```

Cả 3 queue đều còn 0 message, nghĩa là mọi message đã được consumer nhận và ack.

**Kiểm tra đầu vào sai**: gửi một mức không có trong danh sách thì producer báo lỗi và không gửi:

```
> python alert_producer_bai3.py danger "x"
Muc canh bao khong hop le: danger. Chon mot trong ('info', 'warning', 'critical')
```

## 7. Đối chiếu tiêu chí đánh giá

| Tiêu chí | Kết quả | Bằng chứng |
|---|---|---|
| Tạo được exchange | Đạt | `iot_alert_exchange` kiểu `direct` trong `list_exchanges` |
| Bind queue đúng routing key | Đạt | `warning_queue ← warning`, `critical_queue ← critical` trong `list_bindings` |
| Message được phân phối đúng nơi nhận | Đạt | `warning` chỉ tới `warning_queue`, `critical` chỉ tới `critical_queue`, `info` không tới queue nào trong hai queue này |
| Mở rộng: consumer nhận tất cả cảnh báo bằng topic exchange | Đạt | `all_alert_queue` (key `alert.#`) nhận đủ 5/5 message |
| Mở rộng: ghi log cảnh báo ra file | Đạt | `logs/warning_queue.log`, `logs/critical_queue.log`, `logs/all_alert_queue.log` |
