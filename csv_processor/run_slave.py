# run_slave.py
from slave.worker import SlaveWorker
import sys
import uuid

if __name__ == '__main__':
    # Get a worker ID from command-line arguments or generate one
    worker_id = sys.argv[1] if len(sys.argv) > 1 else str(uuid.uuid4())[:8]
    
    print(f"Starting worker with ID: {worker_id}")
    print(f"This worker will process CSV tasks from RabbitMQ and send results back to the master")
    print(f"Press Ctrl+C to stop the worker")
    
    # Create and start the worker
    worker = SlaveWorker(worker_id=worker_id)
    worker.run()