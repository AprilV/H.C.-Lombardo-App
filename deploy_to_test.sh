#!/bin/bash
# Deploy Changes to Test Environment
# Usage: bash deploy_to_test.sh

set -e

TEST_IP="100.48.43.144"

echo "=============================================="
echo "DEPLOYING TO TEST ENVIRONMENT"
echo "=============================================="
echo "Test Instance: $TEST_IP"
echo ""

# Pull latest test branch
echo "[1/3] Pulling latest test branch..."
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@$TEST_IP "cd /home/ubuntu/H.C.-Lombardo-App && git fetch origin test && git checkout test && git pull origin test"

# Restart service
echo "[2/3] Restarting test service..."
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@$TEST_IP "sudo systemctl restart hc-lombardo-test.service"

# Wait for service to start
echo "[3/3] Waiting for service to start..."
sleep 3

# Check status
echo ""
echo "Service Status:"
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@$TEST_IP "sudo systemctl status hc-lombardo-test.service --no-pager -l"

echo ""
echo "Health Check:"
curl -s http://$TEST_IP:5000/health | python3 -m json.tool || echo "Health check failed"

echo ""
echo "=============================================="
echo "DEPLOYMENT COMPLETE"
echo "=============================================="
echo "Test API: http://$TEST_IP:5000"
echo ""
