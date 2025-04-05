# publish_csv.py
import pika
import json
import uuid
import time
import sys

def publish_csv(csv_content, host='localhost', queue='csv_tasks'):
    # Connect to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
    channel = connection.channel()
    
    # Declare the queue
    channel.queue_declare(queue=queue, durable=True)
    
    # Create a message with a unique ID
    message_id = str(uuid.uuid4())
    message = {
        'id': message_id,
        'timestamp': time.time(),
        'csv_content': csv_content
    }
    
    # Publish the message
    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make message persistent
            message_id=message_id
        )
    )
    
    print(f"Published message with ID: {message_id}")
    
    # Close the connection
    connection.close()

if __name__ == '__main__':
    # Read CSV content from file if provided, otherwise use a sample
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            csv_content = f.read()
    else:
        # Sample CSV content
        csv_content = """name,age,city
John,30,New York
Alice,25,Boston
Bob,35,Chicago
Eve,28,San Francisco
"""
    
    publish_csv(csv_content)