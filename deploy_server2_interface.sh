#!/bin/bash
# Deploy Script for Server 2: Interface Server

echo "=========================================="
echo "Deploying Server 2: Interface Server"
echo "=========================================="

# Prompt for Redis server IP
echo ""
read -p "Enter Redis server IP address (Server 1): " REDIS_IP

# Set environment variables
export REDIS_HOST=$REDIS_IP
export REDIS_PORT=6379
export REDIS_DB=0

echo ""
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

echo ""
echo "Testing Redis connection..."
python3 -c "
from redis import Redis
try:
    r = Redis(host='$REDIS_IP', port=6379, db=0)
    r.ping()
    print('✓ Successfully connected to Redis at $REDIS_IP:6379')
except Exception as e:
    print(f'❌ Could not connect to Redis: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "Server 2 deployment complete!"
    echo "Starting Interface Server on port 5001..."
    echo "=========================================="
    echo ""

    # Start interface server
    python3 interface_server.py
else
    echo ""
    echo "❌ Deployment failed. Please check Redis connection."
    echo "   Make sure Server 1 (Redis) is running and accessible."
    exit 1
fi
