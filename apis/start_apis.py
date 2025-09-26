#!/usr/bin/env python3
"""
API Launcher
Start both APIs with proper configuration
"""

import subprocess
import sys
import time
import os
from threading import Thread

def start_api(script_name, port, name):
    """Start an API server"""
    print(f"Starting {name} on port {port}...")
    try:
        result = subprocess.run([
            sys.executable, script_name
        ], cwd=os.path.dirname(__file__))
        if result.returncode != 0:
            print(f"❌ {name} failed to start")
    except KeyboardInterrupt:
        print(f"\n🛑 {name} stopped")
    except Exception as e:
        print(f"❌ Error starting {name}: {e}")

def main():
    """Launch both APIs"""
    print("🚀 Starting H.C. Lombardo App APIs")
    print("=" * 50)
    
    # Check if API files exist
    text_api = "text_classification_api.py"
    nfl_api = "nfl_betting_api.py"
    
    if not os.path.exists(text_api):
        print(f"❌ {text_api} not found")
        return
    
    if not os.path.exists(nfl_api):
        print(f"❌ {nfl_api} not found")
        return
    
    print("Starting APIs in parallel...")
    print("📱 Text Classification API: http://localhost:8000/docs")
    print("🏈 NFL Betting API: http://localhost:8001/docs")
    print("\nPress Ctrl+C to stop both APIs")
    print("-" * 50)
    
    # Start both APIs in separate threads
    text_thread = Thread(
        target=start_api, 
        args=(text_api, 8000, "Text Classification API"),
        daemon=True
    )
    
    nfl_thread = Thread(
        target=start_api,
        args=(nfl_api, 8001, "NFL Betting API"),
        daemon=True
    )
    
    try:
        text_thread.start()
        time.sleep(2)  # Stagger startup
        nfl_thread.start()
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down APIs...")
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()