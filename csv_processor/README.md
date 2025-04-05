# Distributed CSV Processor

This project implements a distributed CSV processing system with a master-slave architecture. It uses RabbitMQ for messaging, Flask for HTTP routing, Flask-SocketIO for real-time communication, and Streamlit for the dashboard.

## Architecture

- **Master Node**: Coordinates the system and exposes a Flask API and SocketIO server.
- **Slave Nodes**: Process CSV data and send results back to the master.
- **RabbitMQ**: Provides message queues for task distribution and result collection.
- **Streamlit Dashboard**: Displays processed CSV data in real-time.

## Setup

### Prerequisites

- Python 3.6+
- RabbitMQ server

### Installation

1. Clone the repository:
git clone <repository-url>
cd csv_processor
Copy
2. Create and activate a virtual environment:
python3 -m venv venv
source venv/bin/activate
Copy
3. Install dependencies:
pip install -r requirements.txt
Copy
4. Ensure RabbitMQ is running:
sudo systemctl start rabbitmq-server
Copy
## Running the System

1. Start the master node:
python run_master.py
Copy
2. Start one or more slave nodes:
python run_slave.py worker1
python run_slave.py worker2
Add more workers as needed
Copy
3. Start the Streamlit dashboard:
python run_dashboard.py
Copy
4. Publish a CSV message:
python publish_csv.py [path-to-csv-file]
Copy
## Design Decisions

- **Idempotency**: Both master and slave nodes track processed message IDs to avoid processing duplicates.
- **Error Handling**: Messages are requeued on processing errors with a limit on retry attempts.
- **Scalability**: Slave nodes can be easily added to scale out processing capacity.
- **Real-time Updates**: SocketIO provides immediate updates to the dashboard when new data is processed.

## Testing

Each component was tested individually:

- RabbitMQ Consumer: Tested by publishing messages and verifying consumption.
- Flask API: Tested using curl and browser requests.
- SocketIO: Tested using the Streamlit dashboard connection.
- CSV Processing: Tested with various CSV formats and error cases.
- Distributed Workers: Tested by running multiple worker instances.
- Streamlit Dashboard: Tested by observing real-time updates.

## Hidden Challenge Solution

The system implements message idempotency by tracking processed message IDs. This prevents duplicate processing if a message is received multiple times, which can happen in distributed messaging systems due to various failure scenarios.
Step 8: Create a Requirements File
Copy# requirements.txt
Flask==2.0.1
Flask-SocketIO==5.1.1
pika==1.2.0
streamlit==1.8.1
pandas==1.3.3
requests==2.26.0
python-socketio==5.5.0