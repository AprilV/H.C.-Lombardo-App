"""
STEP 2C: Flask Server with Keepalive
Try running Flask with explicit threading and no auto-reload
"""
from flask import Flask, jsonify
import sys
import time

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({"message": "Hello from Flask", "status": "running"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "port": 5001})

@app.route('/shutdown')
def shutdown():
    """Endpoint to gracefully shut down the server"""
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        return jsonify({"error": "Not running with Werkzeug server"}), 500
    func()
    return jsonify({"message": "Server shutting down..."})

def run_server():
    """Run the server with explicit settings"""
    print("=" * 60, flush=True)
    print("STEP 2C: FLASK SERVER WITH KEEPALIVE", flush=True)
    print("=" * 60, flush=True)
    print(f"Server starting on http://127.0.0.1:5001", flush=True)
    print(f"Process ID: {os.getpid()}", flush=True)
    print(f"Test with: curl http://127.0.0.1:5001/health", flush=True)
    print("=" * 60, flush=True)
    
    # Force stdout to flush
    sys.stdout.flush()
    
    try:
        # Run with threaded=True to handle multiple requests
        app.run(
            host='127.0.0.1',
            port=5001,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n✓ Server stopped by user", flush=True)
    except Exception as e:
        print(f"\n✗ Server error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    import os
    run_server()
