# master/socketio_handler.py
from master.app import socketio

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print('Client disconnected')

def emit_csv_update(data):
    """
    Emit a CSV update event to all connected clients.
    
    Args:
        data (list): List of dictionaries representing CSV data
    """
    socketio.emit('csv_update', data)