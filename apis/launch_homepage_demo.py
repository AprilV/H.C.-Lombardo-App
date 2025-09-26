#!/usr/bin/env python3
"""
FastAPI Homepage Demo Launcher
Launch APIs with new HTML homepages for demonstration
"""

import subprocess
import time
import webbrowser
from threading import Thread
import sys

def launch_nfl_api():
    """Launch NFL Betting API"""
    print("🏈 Starting NFL Betting API on port 8001...")
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "nfl_betting_api:app", 
            "--host", "0.0.0.0", 
            "--port", "8001", 
            "--reload"
        ], cwd=".", check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting NFL API: {e}")
    except KeyboardInterrupt:
        print("🛑 NFL API stopped")

def launch_text_api():
    """Launch Text Classification API"""
    print("🤖 Starting Text Classification API on port 8000...")
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "text_classification_api:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], cwd=".", check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting Text API: {e}")
    except KeyboardInterrupt:
        print("🛑 Text API stopped")

def open_browsers():
    """Open browsers to show homepages after APIs start"""
    print("⏳ Waiting for APIs to start...")
    time.sleep(3)
    
    print("🌐 Opening API homepages in browser...")
    try:
        webbrowser.open("http://localhost:8001/")  # NFL API
        time.sleep(1)
        webbrowser.open("http://localhost:8000/")  # Text API
        print("✅ Browsers opened successfully")
    except Exception as e:
        print(f"❌ Error opening browsers: {e}")

def main():
    """Launch both APIs with HTML homepages"""
    print("🚀 FastAPI Homepage Demo Launcher")
    print("=" * 45)
    print("📋 Features:")
    print("   • HTML homepages with CSS styling")
    print("   • Clickable navigation to all endpoints")
    print("   • Links to /docs and /redoc documentation")
    print("   • Professional API interfaces")
    print()
    
    print("🎯 Starting APIs...")
    print("   NFL Betting API: http://localhost:8001/")
    print("   Text Classification API: http://localhost:8000/")
    print()
    
    try:
        # Ask user which API to launch
        choice = input("Launch which API? (1=NFL, 2=Text, 3=Both, 0=Exit): ").strip()
        
        if choice == "1":
            # Launch NFL API only
            Thread(target=open_browsers, daemon=True).start()
            launch_nfl_api()
            
        elif choice == "2":  
            # Launch Text API only
            Thread(target=open_browsers, daemon=True).start()
            launch_text_api()
            
        elif choice == "3":
            # Launch both APIs
            print("🔄 Starting both APIs in parallel...")
            print("⚠️ Note: This will run both APIs simultaneously")
            print("💡 Use Ctrl+C to stop servers")
            
            # Start browser opener
            Thread(target=open_browsers, daemon=True).start()
            
            # Start APIs in threads
            nfl_thread = Thread(target=launch_nfl_api, daemon=True)
            text_thread = Thread(target=launch_text_api, daemon=True)
            
            nfl_thread.start()
            text_thread.start()
            
            print("✅ Both APIs started!")
            print("🌐 Check your browser for the homepages")
            print("📚 API Documentation:")
            print("   NFL: http://localhost:8001/docs")
            print("   Text: http://localhost:8000/docs")
            
            # Keep main thread alive
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Shutting down APIs...")
                
        elif choice == "0":
            print("👋 Exiting...")
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()