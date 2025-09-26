#!/usr/bin/env python3
"""
Simple HTTP Server to Demo FastAPI Homepage
Shows what your FastAPI homepage looks like
"""

import http.server
import socketserver
import webbrowser
import threading
import time
import os

PORT = 8080

def start_server():
    """Start simple HTTP server"""
    os.chdir(os.path.dirname(__file__))
    
    Handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🌐 Server running at http://localhost:{PORT}")
        print(f"📋 Serving FastAPI Homepage Demo")
        print(f"🛑 Press Ctrl+C to stop")
        httpd.serve_forever()

def open_browser():
    """Open browser after server starts"""
    time.sleep(2)
    webbrowser.open(f"http://localhost:{PORT}/fastapi_homepage_demo.html")
    print("✅ Browser opened to show your FastAPI homepage!")

def main():
    print("🚀 FastAPI Homepage Demo Server")
    print("=" * 40)
    print("This shows you exactly what your FastAPI homepage looks like")
    print("when served by the FastAPI root ('/') route")
    
    # Start browser opener in background
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")

if __name__ == "__main__":
    main()