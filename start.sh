#!/bin/bash
# EC2 Production Startup Script
# This script starts the Gunicorn API server on EC2

# Start gunicorn on port 5000 (Nginx proxies to this)
exec gunicorn api_server:app --bind 0.0.0.0:5000 --workers 2 --timeout 120
