#!/bin/bash
# Deploy Script for Server 3: AI Worker

echo "=========================================="
echo "Deploying Server 3: AI Worker"
echo "=========================================="

# Prompt for Redis server IP
echo ""
read -p "Enter Redis server IP address (Server 1): " REDIS_IP

# Set environment variables
export REDIS_HOST=$REDIS_IP
export REDIS_PORT=6379
export REDIS_DB=0

# Check for Google Cloud credentials
echo ""
if [ -f "credentials.json" ]; then
    export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/credentials.json"
    echo "✓ Found credentials.json"
else
    read -p "Enter path to Google Cloud credentials.json: " CRED_PATH
    export GOOGLE_APPLICATION_CREDENTIALS=$CRED_PATH
fi

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
    read -p "How many worker instances to start? (1-5): " WORKER_COUNT
    WORKER_COUNT=${WORKER_COUNT:-1}

    echo ""
    echo "=========================================="
    echo "Server 3 deployment complete!"
    echo "Starting $WORKER_COUNT AI Worker(s)..."
    echo "=========================================="
    echo ""

    # Start workers
    for i in $(seq 1 $WORKER_COUNT); do
        echo "Starting Worker $i..."
        python3 start_worker.py &
        sleep 2
    done

    echo ""
    echo "All workers started!"
    echo "Press Ctrl+C to stop all workers"

    # Wait for all background processes
    wait
else
    echo ""
    echo "❌ Deployment failed. Please check Redis connection."
    echo "   Make sure Server 1 (Redis) is running and accessible."
    exit 1
fi
