"""Bai 3 - Alert Producer
Gui canh bao IoT vao direct exchange 'iot_alert_exchange' voi routing key
info / warning / critical.

Mo rong: dong thoi gui ban sao vao topic exchange 'iot_alert_topic_exchange'
voi routing key 'alert.<muc>' de consumer tong hop (all_alert_consumer_bai3.py)
nhan tat ca canh bao.

Cach chay:
    python alert_producer_bai3.py                      # gui 3 canh bao mau
    python alert_producer_bai3.py warning "Noi dung"   # gui 1 canh bao tuy chon
"""
import os
import sys
from datetime import datetime

import pika

SINH_VIEN = "Vu Thanh Nguyen - B23DCCN617"

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")

EXCHANGE = "iot_alert_exchange"
TOPIC_EXCHANGE = "iot_alert_topic_exchange"
LEVELS = ("info", "warning", "critical")

SAMPLE_ALERTS = [
    ("info", "Cam bien phong may 1 gui du lieu binh thuong info"),
    ("warning", "Nhiet do phong may vuot nguong warning"),
    ("critical", "Cam bien kho lanh mat ket noi critical"),
]


def main():
    if len(sys.argv) == 3:
        level, message = sys.argv[1].lower(), sys.argv[2]
        if level not in LEVELS:
            print(f"Muc canh bao khong hop le: {level}. Chon mot trong {LEVELS}")
            sys.exit(1)
        alerts = [(level, message)]
    elif len(sys.argv) == 1:
        alerts = SAMPLE_ALERTS
    else:
        print(__doc__)
        sys.exit(1)

    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials)
    )
    channel = connection.channel()

    channel.exchange_declare(exchange=EXCHANGE, exchange_type="direct", durable=True)
    channel.exchange_declare(exchange=TOPIC_EXCHANGE, exchange_type="topic", durable=True)

    for level, message in alerts:
        body = f"{message} | gui boi {SINH_VIEN} | {datetime.now():%H:%M:%S}"
        props = pika.BasicProperties(content_type="text/plain", delivery_mode=2)

        channel.basic_publish(exchange=EXCHANGE, routing_key=level, body=body.encode(), properties=props)
        channel.basic_publish(
            exchange=TOPIC_EXCHANGE, routing_key=f"alert.{level}", body=body.encode(), properties=props
        )
        print(f"[x] Da gui [{level}] -> {EXCHANGE}: {message}")

    connection.close()


if __name__ == "__main__":
    main()
