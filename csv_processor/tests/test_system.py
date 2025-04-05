# test_system.py
import pika
import json
import uuid
import time
import requests
import sys

def publish_csv(csv_content, host='localhost', queue='csv_tasks'):
    """Publish a CSV message to RabbitMQ"""
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
    
    return message_id

def check_processed_data(message_id=None):
    """Check if the data was processed and available via the API"""
    try:
        response = requests.get("http://localhost:5000/data")
        if response.status_code == 200:
            data = response.json()
            if data:
                print("Data successfully processed and available via API:")
                print(f"Number of rows: {len(data)}")
                print("Sample data:")
                if len(data) > 0:
                    sample = data[0]
                    for key, value in sample.items():
                        print(f"  {key}: {value}")
                
                # Check if the data was processed by a worker
                if len(data) > 0 and 'processed_by' in data[0]:
                    print(f"Data was processed by worker: {data[0]['processed_by']}")
                
                return True
            else:
                print("No data available via API yet")
                return False
        else:
            print(f"Error fetching data: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error connecting to the server: {str(e)}")
        return False

def run_test():
    """Run a full system test"""
    print("Starting system test...")
    
    # Sample CSV content
    csv_content = """name,age,city,occupation
John Doe,30,New York,Engineer
Jane Smith,25,San Francisco,Designer
Bob Johnson,45,Chicago,Manager
Alice Brown,33,Boston,Developer
Eve Wilson,29,Seattle,Analyst
"""
    
    print("\n1. Publishing CSV message to RabbitMQ...")
    message_id = publish_csv(csv_content)
    
    print("\n2. Waiting for processing...")
    for i in range(10):
        print(f"Checking data (attempt {i+1}/10)...")
        if check_processed_data(message_id):
            print("\nTest successful! The CSV was processed correctly.")
            return
        time.sleep(1)
    
    print("\nTest failed: Data was not processed within the timeout period.")

if __name__ == "__main__":
    run_test()