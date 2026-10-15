"""Bai 3 - Warning Consumer
Tao queue 'warning_queue', bind voi exchange 'iot_alert_exchange' bang
routing key 'warning'. Chi nhan canh bao muc warning. Ghi log ra file logs/<ten_queue>.log.

Cach chay:
    python warning_consumer_bai3.py     (dung bang Ctrl+C)
"""
import os
import sys
from datetime import datetime

import pika

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")

EXCHANGE = "iot_alert_exchange"
QUEUE = "warning_queue"
ROUTING_KEY = "warning"
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, f"{QUEUE}.log")  # moi consumer 1 file, tranh ghi de khi chay song song


def on_message(channel, method, properties, body):
    message = body.decode()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{QUEUE}] Da nhan: {message}")
    print(f"    routing key: {method.routing_key} | thoi gian nhan: {now}")
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{now} [{QUEUE}] [{method.routing_key}] {message}\n")
    channel.basic_ack(delivery_tag=method.delivery_tag)


def main():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials)
    )
    channel = connection.channel()

    channel.exchange_declare(exchange=EXCHANGE, exchange_type="direct", durable=True)
    channel.queue_declare(queue=QUEUE, durable=True)
    channel.queue_bind(exchange=EXCHANGE, queue=QUEUE, routing_key=ROUTING_KEY)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE, on_message_callback=on_message)

    print(f"[*] {QUEUE} dang lang nghe {EXCHANGE} (routing key='{ROUTING_KEY}'). Nhan Ctrl+C de dung.")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\n[!] Dung consumer.")
        channel.stop_consuming()
    finally:
        connection.close()
        sys.exit(0)


if __name__ == "__main__":
    main()
