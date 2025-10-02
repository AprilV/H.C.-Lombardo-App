#!/usr/bin/env python3
"""
Minimal FastAPI test for database status
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import sys
import os

# Add the apis directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'apis'))

app = FastAPI()

@app.get("/test-db")
async def test_database_status():
    """Simple test of database status"""
    try:
        from live_data_collector import LiveNFLDataCollector
        collector = LiveNFLDataCollector()
        
        return JSONResponse(content={
            "status": "success",
            "message": "Database connection successful",
            "db_path": collector.db_path
        })
        
    except Exception as e:
        return JSONResponse(content={
            "status": "error", 
            "message": f"Error: {str(e)}"
        }, status_code=500)

if __name__ == "__main__":
    import uvicorn
    print("🧪 Starting minimal FastAPI test server...")
    uvicorn.run(app, host="127.0.0.1", port=8005)