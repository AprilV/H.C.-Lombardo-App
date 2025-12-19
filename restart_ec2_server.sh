#!/bin/bash
# Restart API server on EC2

echo "Stopping existing API server..."
pkill -f api_server.py || true
sleep 2

echo "Starting API server..."
cd /home/ubuntu/H.C.-Lombardo-App
source venv/bin/activate
nohup python api_server.py > logs/api_restart.log 2>&1 &

sleep 3

echo "Checking server status..."
curl -s http://localhost:5000/health || echo "Server not responding yet"

echo "Done!"
