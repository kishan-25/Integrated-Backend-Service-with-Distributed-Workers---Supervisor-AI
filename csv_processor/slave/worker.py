# slave/worker.py
import pika
import json
import time
import uuid
from datetime import datetime
import io
import csv

class SlaveWorker:
    """Slave worker that processes CSV tasks."""
    
    def __init__(self, host='localhost', tasks_queue='csv_tasks', results_queue='csv_results', worker_id=None):
        self.host = host
        self.tasks_queue = tasks_queue
        self.results_queue = results_queue
        self.worker_id = worker_id or str(uuid.uuid4())
        self.connection = None
        self.channel = None
        
        # Set of message IDs that have been processed (for idempotency)
        self.processed_message_ids = set()
        
    def setup(self):
        """Set up the RabbitMQ connection and channels."""
        print(f"Worker {self.worker_id} connecting to RabbitMQ at {self.host}...")
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))
        self.channel = self.connection.channel()
        
        print(f"Worker {self.worker_id} declaring queues...")
        # Declare the tasks queue
        self.channel.queue_declare(queue=self.tasks_queue, durable=True)
        
        # Declare the results queue
        self.channel.queue_declare(queue=self.results_queue, durable=True)
        
        # Set prefetch count to 1 to ensure fair dispatch
        self.channel.basic_qos(prefetch_count=1)
        
        print(f"Worker {self.worker_id} setting up consumer...")
        # Set up the consumer for the tasks queue
        self.channel.basic_consume(
            queue=self.tasks_queue,
            on_message_callback=self.on_message,
            auto_ack=False
        )
        
        print(f"Worker {self.worker_id} setup complete and ready to process messages.")
        
    def parse_csv(self, csv_content):
        """
        Parse CSV content into a list of dictionaries.
        
        Args:
            csv_content (str): CSV content as a string
            
        Returns:
            list: List of dictionaries, where each dictionary represents a row in the CSV
        """
        try:
            # Create a file-like object from the CSV string
            csv_file = io.StringIO(csv_content)
            
            # Parse the CSV file
            reader = csv.DictReader(csv_file)
            
            # Convert to list of dictionaries
            rows = [row for row in reader]
            
            # Add processing metadata
            for row in rows:
                row['processed_by'] = self.worker_id
                row['processed_at'] = datetime.now().isoformat()
                
            return rows
        except Exception as e:
            raise ValueError(f"Error parsing CSV: {str(e)}")
            
    def on_message(self, ch, method, properties, body):
        """
        Callback for when a message is received.
        
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
            
            # Check if this message has already been processed
            if message_id in self.processed_message_ids:
                print(f"Message {message_id} already processed, skipping")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
                
            print(f"Worker {self.worker_id} processing message {message_id}")
            
            # Simulate processing time
            time.sleep(1)
            
            # Process the CSV content
            processed_data = self.parse_csv(csv_content)
            
            # Create a result message
            result = {
                'id': message_id,
                'worker_id': self.worker_id,
                'processed_at': datetime.now().isoformat(),
                'processed_data': processed_data
            }
            
            print(f"Worker {self.worker_id} sending results for message {message_id}")
            # Publish the result to the results queue
            self.channel.basic_publish(
                exchange='',
                routing_key=self.results_queue,
                body=json.dumps(result),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    message_id=message_id
                )
            )
            
            # Add the message ID to the set of processed messages
            self.processed_message_ids.add(message_id)
            
            # Acknowledge the message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
            print(f"Worker {self.worker_id} completed processing message {message_id}")
            
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            # Reject the message and requeue it
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            
    def start_consuming(self):
        """Start consuming messages."""
        print(f"Worker {self.worker_id} starting to consume messages from queue '{self.tasks_queue}'...")
        print(f"Waiting for messages. To exit press CTRL+C")
        self.channel.start_consuming()
        
    def run(self):
        """Run the worker."""
        self.setup()
        self.start_consuming()