#!/bin/bash
# Quick AWS deployment - skip system upgrades

echo "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt-get install -y nodejs

echo "Installing PostgreSQL..."
sudo apt-get install -y postgresql postgresql-contrib python3-pip python3-venv git

echo "Setting up database..."
sudo -u postgres psql -c "CREATE DATABASE nfl_analytics;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE USER nfl_user WITH PASSWORD 'aprilv120';" 2>/dev/null || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE nfl_analytics TO nfl_user;"
sudo -u postgres psql -c "ALTER DATABASE nfl_analytics OWNER TO nfl_user;"

echo "Cloning repository..."
cd /home/ubuntu
git clone https://github.com/AprilV/H.C.-Lombardo-App.git 2>/dev/null || (cd H.C.-Lombardo-App && git pull)
cd H.C.-Lombardo-App

echo "Installing Python packages..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install flask flask-cors psycopg2-binary python-dotenv requests beautifulsoup4 pandas scikit-learn gunicorn

echo "Building React..."
cd frontend
npm install --legacy-peer-deps
npm run build
cd ..

echo "Creating service..."
sudo tee /etc/systemd/system/hc-lombardo.service > /dev/null <<'EOF'
[Unit]
Description=HC Lombardo App
After=postgresql.service

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/H.C.-Lombardo-App
Environment="PATH=/home/ubuntu/H.C.-Lombardo-App/venv/bin"
Environment="DB_NAME=nfl_analytics"
Environment="DB_USER=nfl_user"
Environment="DB_PASSWORD=aprilv120"
Environment="DB_HOST=localhost"
ExecStart=/home/ubuntu/H.C.-Lombardo-App/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 api_server:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable hc-lombardo
sudo systemctl start hc-lombardo

echo "DONE! App at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):5000"
