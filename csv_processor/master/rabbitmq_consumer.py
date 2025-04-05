# master/rabbitmq_consumer.py
import pika
import json
from master.csv_processor import parse_csv, validate_csv
from master.socketio_handler import emit_csv_update
import threading
import time

class RabbitMQConsumer:
    """RabbitMQ consumer that listens for CSV processing tasks."""
    
    def __init__(self, host='localhost', queue_name='csv_tasks', result_queue='csv_results'):
        self.host = host
        self.queue_name = queue_name
        self.result_queue = result_queue
        self.connection = None
        self.channel = None
        self.processed_data = []
        
        # Set of message IDs that have been processed (for idempotency)
        self.processed_message_ids = set()
        
    def setup(self):
        """Set up the RabbitMQ connection and channels."""
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))
        self.channel = self.connection.channel()
        
        # Declare the tasks queue
        self.channel.queue_declare(queue=self.queue_name, durable=True)
        
        # Declare the results queue for receiving processed results from slaves
        self.channel.queue_declare(queue=self.result_queue, durable=True)
        
        # Set up the consumer for the tasks queue
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.on_message,
            auto_ack=False  # We'll manually acknowledge messages
        )
        
        # Set up the consumer for the results queue
        self.channel.basic_consume(
            queue=self.result_queue,
            on_message_callback=self.on_result,
            auto_ack=False
        )
        
    def on_message(self, ch, method, properties, body):
        """
        Callback for when a message is received from the tasks queue.
        
        Args:
            ch: Channel
            method: Method
            properties: Properties
            body: Message body
        """
        try:
            # Parse the message
            message = json.loads(body)
            
            # Extract message ID and CSV content
            message_id = message.get('id')
            csv_content = message.get('csv_content')
            
            # Check if this message has already been processed (idempotency)
            if message_id in self.processed_message_ids:
                print(f"Message {message_id} already processed, skipping")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
                
            # Process the CSV content
            csv_data = parse_csv(csv_content)
            
            # Validate the CSV data
            if not validate_csv(csv_data):
                print("Invalid CSV data")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
                
            # Store the processed data and emit a SocketIO event
            from master.app import processed_data
            processed_data.clear()
            processed_data.extend(csv_data)
            
            # Emit the CSV update event
            emit_csv_update(csv_data)
            
            # Add the message ID to the set of processed messages
            self.processed_message_ids.add(message_id)
            
            # Acknowledge the message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            # Reject the message and requeue it
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            
    def on_result(self, ch, method, properties, body):
        """
        Callback for when a result message is received from the results queue.
        
        Args:
            ch: Channel
            method: Method
            properties: Properties
            body: Message body
        """
        try:
            # Parse the result message
            result = json.loads(body)
            
            # Extract message ID and processed data
            message_id = result.get('id')
            slave_data = result.get('processed_data')
            
            # Check if this message has already been processed
            if message_id in self.processed_message_ids:
                print(f"Result for message {message_id} already processed, skipping")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
                
            # Update the master's data with the slave's processed data
            from master.app import processed_data
            processed_data.clear()
            processed_data.extend(slave_data)
            
            # Emit the CSV update event
            emit_csv_update(slave_data)
            
            # Add the message ID to the set of processed messages
            self.processed_message_ids.add(message_id)
            
            # Acknowledge the message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            print(f"Error processing result: {str(e)}")
            # Reject the message
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            
    def start_consuming(self):
        """Start consuming messages."""
        print("Starting to consume messages...")
        self.channel.start_consuming()
        
    def run(self):
        """Run the consumer in a separate thread."""
        self.setup()
        
        # Start consuming in a separate thread
        consumer_thread = threading.Thread(target=self.start_consuming)
        consumer_thread.daemon = True
        consumer_thread.start()