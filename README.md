# Distributed CSV Processing System

This project implements a **distributed system** for processing CSV files using a **master-slave architecture** with:

- 📨 **RabbitMQ** for messaging  
- 🌐 **Flask** for API endpoints  
- ⚡ **Flask-SocketIO** for real-time updates  
- 📊 **Streamlit** for the dashboard

---

## 🚀 Architecture Overview

### 🧠 Master Node
- Runs a Flask server with REST API endpoints
- Manages Socket.IO connections for real-time updates
- Consumes processed results from slave nodes

### 🛠️ Slave Nodes
- Process CSV data independently
- Can be scaled horizontally
- Send results back to the master via RabbitMQ

### 📬 RabbitMQ
- Acts as a message broker
- Manages task queue for CSV processing
- Distributes tasks to available slave nodes

### 📈 Streamlit Dashboard
- Real-time visualization of processed data
- Connects to master via HTTP and Socket.IO

---

## ⚙️ Setup Instructions

### 🧾 Prerequisites
- Python 3.8+
- RabbitMQ Server

### 📦 Required Python Packages

Install dependencies:

```bash
pip install -r requirements.txt
```
Start RabbitMQ Server
On Ubuntu/Debian:

```bash
sudo service rabbitmq-server start
```

On macOS with Homebrew:
```bash
brew services start rabbitmq
```

🔧 Running the System
1️⃣ Start the Master Node

```bash
python run_master.py
```

2️⃣ Start One or More Slave Nodes
```bash
python run_slave.py slave1
python run_slave.py slave2
```
# Add more as needed
3️⃣ Start the Streamlit Dashboard

```bash
python run_dashboard.py
# or
streamlit run streamlit_app/dashboard.py
```

4️⃣ Publish a CSV File for Processing
```bash
python publish_csv.py your_data.csv
```

📁 System Components
📡 Master Node
Key Files:

master/app.py: Flask app with API endpoints

master/socketio_handler.py: Handles Socket.IO connections

master/rabbitmq_consumer.py: Consumes results from RabbitMQ

master/csv_processor.py: CSV utility functions

🧵 Slave Nodes
Key File:
```bash
slave/worker.py: Processes CSV tasks from RabbitMQ and returns results
```
📊 Streamlit Dashboard
Key File:
```bash
streamlit_app/dashboard.py: Real-time UI for processed data
```
✅ Testing
Run Full Test Suite

```bash
python run_tests.py
```
Run Individual Tests
```bash
python tests/test_csv_processor.py
python tests/test_flask_api.py
python tests/test_idempotency.py
python tests/test_stress.py
python tests/test_system.py
```
📐 Design Decisions & Trade-offs
🔁 Message Handling
Idempotency: Unique IDs for all messages to avoid duplication

Durability: Messages survive broker restarts

Manual Acknowledgment: Only remove message after successful processing

🧮 Data Consistency
Master node stores latest processed state

Updates fully replace previous data

⚡ Real-time Updates
Socket.IO used for immediate dashboard updates

Polling fallback for robustness

🛡️ Error Handling
API error handlers in place

Failed tasks requeued

HTTP status codes well-managed

📈 Scalability
Horizontally scalable slave nodes

RabbitMQ fair dispatch ensures balanced task load

🧠 Conclusion
This distributed system demonstrates how to build a scalable CSV processing pipeline using:

Python

RabbitMQ

Flask

Streamlit

Master-slave architecture allows horizontal scaling and real-time visibility into the processing pipeline via the dashboard.

