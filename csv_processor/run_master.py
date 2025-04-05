# run_master.py
from master.app import app, socketio
from master.rabbitmq_consumer import RabbitMQConsumer
import threading
import time

if __name__ == '__main__':
    # Create and start the RabbitMQ consumer
    consumer = RabbitMQConsumer()
    consumer.run()
    
    # Start the Flask SocketIO server
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)