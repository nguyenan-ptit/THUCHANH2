import json
import random
import time

import pika


HOST = "localhost"
PORT = 5672
VIRTUAL_HOST = "/"
USERNAME = "guest"
PASSWORD = "guest"
QUEUE_NAME = "sensor_data_queue"


def main():
    connection = None
    try:
        # Ket noi RabbitMQ bang tai khoan cua broker.
        credentials = pika.PlainCredentials(USERNAME, PASSWORD)
        parameters = pika.ConnectionParameters(
            host=HOST,
            port=PORT,
            virtual_host=VIRTUAL_HOST,
            credentials=credentials,
        )
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        # Khai bao queue voi thuoc tinh mac dinh, giong consumer.
        channel.queue_declare(queue=QUEUE_NAME)
        print("Sensor producer dang chay. Nhan Ctrl+C de dung.")

        while True:
            payload = {
                "device_id": "sensor01",
                "temperature": round(random.uniform(20.0, 40.0), 1),
                "humidity": round(random.uniform(30.0, 80.0), 1),
            }
            message = json.dumps(payload)

            # Gui JSON UTF-8 qua default exchange, moi 3 giay.
            channel.basic_publish(
                exchange="",
                routing_key=QUEUE_NAME,
                body=message.encode("utf-8"),
            )
            print(f"Da gui: {message}")
            time.sleep(3)
    except KeyboardInterrupt:
        print("\nDa dung sensor producer.")
    except (pika.exceptions.AMQPError, OSError) as error:
        print(f"Loi RabbitMQ tai {HOST}:{PORT}: {error!r}")
        return 1
    finally:
        if connection is not None and connection.is_open:
            connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
