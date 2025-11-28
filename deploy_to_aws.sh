#!/bin/bash
# AWS EC2 Deployment Script for HC Lombardo App

set -e  # Exit on any error

echo "==================================="
echo "HC Lombardo App - AWS Deployment"
echo "==================================="

# Update system
echo "[1/10] Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Python 3.11
echo "[2/10] Installing Python 3.11..."
sudo apt-get install -y python3.11 python3.11-venv python3-pip

# Install Node.js 18
echo "[3/10] Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install PostgreSQL
echo "[4/10] Installing PostgreSQL..."
sudo apt-get install -y postgresql postgresql-contrib

# Install Git
echo "[5/10] Installing Git..."
sudo apt-get install -y git

# Clone repository
echo "[6/10] Cloning repository..."
cd /home/ubuntu
git clone https://github.com/AprilV/H.C.-Lombardo-App.git
cd H.C.-Lombardo-App

# Set up PostgreSQL database
echo "[7/10] Setting up PostgreSQL database..."
sudo -u postgres psql -c "CREATE DATABASE nfl_analytics;"
sudo -u postgres psql -c "CREATE USER nfl_user WITH PASSWORD 'aprilv120';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE nfl_analytics TO nfl_user;"
sudo -u postgres psql -c "ALTER DATABASE nfl_analytics OWNER TO nfl_user;"

# Install Python dependencies
echo "[8/10] Installing Python dependencies..."
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install flask flask-cors psycopg2-binary python-dotenv requests beautifulsoup4 pandas scikit-learn gunicorn

# Build React frontend
echo "[9/10] Building React frontend..."
cd frontend
npm install
npm run build
cd ..

# Create systemd service
echo "[10/10] Setting up systemd service..."
sudo tee /etc/systemd/system/hc-lombardo.service > /dev/null <<EOF
[Unit]
Description=HC Lombardo NFL Analytics App
After=network.target postgresql.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/H.C.-Lombardo-App
Environment="PATH=/home/ubuntu/H.C.-Lombardo-App/venv/bin"
Environment="DB_NAME=nfl_analytics"
Environment="DB_USER=nfl_user"
Environment="DB_PASSWORD=aprilv120"
Environment="DB_HOST=localhost"
Environment="DB_PORT=5432"
ExecStart=/home/ubuntu/H.C.-Lombardo-App/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 api_server:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable hc-lombardo
sudo systemctl start hc-lombardo

echo ""
echo "==================================="
echo "✅ Deployment Complete!"
echo "==================================="
echo "App running at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):5000"
echo ""
echo "Next steps:"
echo "1. Load database data (run migration script)"
echo "2. Access your app in browser"
echo "==================================="
