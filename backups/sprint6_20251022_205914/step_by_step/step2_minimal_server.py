"""
STEP 2: Minimal Flask Server Test
Create the simplest possible Flask server and verify it actually runs
"""
from flask import Flask, jsonify
import sys

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({"message": "Hello from minimal Flask", "status": "running"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    print("=" * 60)
    print("STEP 2: MINIMAL FLASK SERVER")
    print("=" * 60)
    print("Starting server on http://127.0.0.1:5001")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)
    except Exception as e:
        print(f"\n✗ FAIL: Server failed to start: {e}", file=sys.stderr)
        sys.exit(1)
