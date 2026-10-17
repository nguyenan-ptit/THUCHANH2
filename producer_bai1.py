
import sys
import time
import pika

RABBITMQ_HOST = "localhost"
RABBITMQ_PORT = 5672
RABBITMQ_USER = "guest"
RABBITMQ_PASS = "guest"
QUEUE_NAME = "iot_lab_queue"

HO_TEN = "Dang Ky Vi"
MA_SV = "B23DCCN914"


def main():
    so_message = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    params = pika.ConnectionParameters(
        host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials
    )
    try:
        connection = pika.BlockingConnection(params)
    except pika.exceptions.AMQPConnectionError:
        print(f"Khong the ket noi toi RabbitMQ tai {RABBITMQ_HOST}:{RABBITMQ_PORT}")
        print("Kiem tra RabbitMQ da chay chua (rabbitmq-server / Docker).")
        sys.exit(1)

    channel = connection.channel()

   
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    
    for i in range(1, so_message + 1):
        body = f"Xin chao tu ung dung Python AMQP - {MA_SV} - {HO_TEN}"
        if so_message > 1:
            body += f" (message #{i})"
        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=body.encode("utf-8"),
            properties=pika.BasicProperties(delivery_mode=2), 
        )
        print(f"Da gui message: {body}")
        time.sleep(0.5)

    
    connection.close()


if __name__ == "__main__":
    main()
