#!/bin/bash
# Setup Test Environment - Mirror Production
# Run this ONCE to configure new test EC2 instance
# Usage: bash setup_test_environment.sh

set -e  # Exit on any error

TEST_IP="100.48.43.144"
PROD_IP="34.198.25.249"

echo "=============================================="
echo "HC LOMBARDO TEST ENVIRONMENT SETUP"
echo "=============================================="
echo "Production: $PROD_IP"
echo "Test:       $TEST_IP"
echo "=============================================="
echo ""

# Step 1: Update system packages
echo "[1/9] Updating system packages on test instance..."
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@$TEST_IP "sudo apt-get update -y && sudo apt-get upgrade -y"

# Step 2: Install required software
echo "[2/9] Installing Python 3.12, PostgreSQL 16, Git..."
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@$TEST_IP "sudo apt-get install -y python3 python3-venv python3-pip postgresql postgresql-contrib git curl"

# Step 3: Clone repository
echo "[3/9] Cloning GitHub repository..."
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@$TEST_IP "cd /home/ubuntu && git clone https://github.com/AprilV/H.C.-Lombardo-App.git"

# Step 4: Create test branch
echo "[4/9] Creating test branch..."
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@$TEST_IP "cd /home/ubuntu/H.C.-Lombardo-App && git checkout -b test && git push -u origin test"

# Step 5: Setup PostgreSQL database
echo "[5/9] Setting up PostgreSQL database..."
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@$TEST_IP "sudo -u postgres psql -c \"CREATE DATABASE nfl_analytics;\""
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@$TEST_IP "sudo -u postgres psql -c \"CREATE USER nfl_user WITH PASSWORD 'aprilv120';\""
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@$TEST_IP "sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE nfl_analytics TO nfl_user;\""
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@$TEST_IP "sudo -u postgres psql -c \"ALTER DATABASE nfl_analytics OWNER TO nfl_user;\""

# Step 6: Dump production database and restore to test
echo "[6/9] Cloning production database to test..."
echo "  Dumping production database..."
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@$PROD_IP "pg_dump -U nfl_user -d nfl_analytics -h localhost" > /tmp/nfl_analytics_test_backup.sql

echo "  Uploading to test instance..."
cat /tmp/nfl_analytics_test_backup.sql | ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@$TEST_IP "cat > /tmp/nfl_analytics_backup.sql"

echo "  Restoring database..."
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@$TEST_IP "PGPASSWORD=aprilv120 psql -U nfl_user -d nfl_analytics -h localhost < /tmp/nfl_analytics_backup.sql"

echo "  Cleaning up dump file..."
rm /tmp/nfl_analytics_test_backup.sql
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@$TEST_IP "rm /tmp/nfl_analytics_backup.sql"

# Step 7: Install Python dependencies
echo "[7/9] Installing Python dependencies..."
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@$TEST_IP "cd /home/ubuntu/H.C.-Lombardo-App && python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && pip install gunicorn"

# Step 8: Create systemd service
echo "[8/9] Creating systemd service..."
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@$TEST_IP "sudo tee /etc/systemd/system/hc-lombardo-test.service > /dev/null" << 'EOF'
[Unit]
Description=HC Lombardo App (TEST)
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

# Step 9: Enable and start service
echo "[9/9] Starting test service..."
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@$TEST_IP "sudo systemctl daemon-reload && sudo systemctl enable hc-lombardo-test.service && sudo systemctl start hc-lombardo-test.service"

echo ""
echo "=============================================="
echo "TEST ENVIRONMENT SETUP COMPLETE!"
echo "=============================================="
echo ""
echo "Test API: http://$TEST_IP:5000"
echo ""
echo "Verify service status:"
echo "  ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@$TEST_IP \"sudo systemctl status hc-lombardo-test.service\""
echo ""
echo "Test health endpoint:"
echo "  curl http://$TEST_IP:5000/health"
echo ""
echo "View logs:"
echo "  ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@$TEST_IP \"sudo journalctl -u hc-lombardo-test.service -f\""
echo ""
