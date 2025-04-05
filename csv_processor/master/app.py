# master/app.py
from flask import Flask, jsonify, request
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Shared data store to hold the most recently processed CSV data
processed_data = []

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})

@app.route('/data', methods=['GET'])
def get_data():
    """Return the most recently processed CSV data."""
    global processed_data
    return jsonify(processed_data)

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500

# SocketIO event handlers will be added in socketio_handler.py

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)