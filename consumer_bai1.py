
import sys
from datetime import datetime
import pika

RABBITMQ_HOST = "localhost"
RABBITMQ_PORT = 5672
RABBITMQ_USER = "guest"
RABBITMQ_PASS = "guest"
QUEUE_NAME = "iot_lab_queue"


def on_message(channel, method, properties, body):
    
    noi_dung = body.decode("utf-8")
    thoi_gian = datetime.now().strftime("%H:%M:%S")
    print(f"Da nhan message: {noi_dung}")
    print(f"Thoi gian nhan: {thoi_gian}")
    print("-" * 50)
    
    channel.basic_ack(delivery_tag=method.delivery_tag)


def main():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    params = pika.ConnectionParameters(
        host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials
    )
    try:
        connection = pika.BlockingConnection(params)
    except pika.exceptions.AMQPConnectionError:
        print(f"Khong the ket noi toi RabbitMQ tai {RABBITMQ_HOST}:{RABBITMQ_PORT}")
        sys.exit(1)

    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)  
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=on_message)

    print(f"Dang lang nghe queue '{QUEUE_NAME}'... Nhan Ctrl+C de dung.")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\nDa dung consumer.")
        channel.stop_consuming()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
