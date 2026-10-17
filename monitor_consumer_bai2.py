import json

import pika


HOST = "localhost"
PORT = 5672
VIRTUAL_HOST = "/"
USERNAME = "guest"
PASSWORD = "guest"
QUEUE_NAME = "sensor_data_queue"


def on_message(channel, method, properties, body):
    try:
        # Giai ma message UTF-8 va doc cac truong JSON.
        payload = json.loads(body.decode("utf-8"))
        device_id = payload["device_id"]
        temperature = payload["temperature"]
        humidity = payload["humidity"]

        print(f"Device: {device_id}")
        print(f"Temperature: {temperature}")
        print(f"Humidity: {humidity}")

        # Hai dieu kien doc lap; co the in ca hai canh bao.
        if temperature > 35:
            print("CANH BAO: Nhiet do cao")
        if humidity < 40:
            print("CANH BAO: Do am thap")
        print()
    except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as error:
        print(f"Message khong hop le, bo qua: {error}")


def main():
    connection = None
    try:
        # Dung cung cau hinh broker voi producer.
        credentials = pika.PlainCredentials(USERNAME, PASSWORD)
        parameters = pika.ConnectionParameters(
            host=HOST,
            port=PORT,
            virtual_host=VIRTUAL_HOST,
            credentials=credentials,
        )
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        # Khai bao cung queue va lang nghe lien tuc.
        channel.queue_declare(queue=QUEUE_NAME)
        channel.basic_consume(
            queue=QUEUE_NAME,
            on_message_callback=on_message,
            auto_ack=True,
        )
        print("Monitoring consumer dang lang nghe. Nhan Ctrl+C de dung.")
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\nDa dung monitoring consumer.")
    except (pika.exceptions.AMQPError, OSError) as error:
        print(f"Loi RabbitMQ tai {HOST}:{PORT}: {error!r}")
        return 1
    finally:
        if connection is not None and connection.is_open:
            connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
