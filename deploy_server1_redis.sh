#!/bin/bash
# Deploy Script for Server 1: Redis Orchestrator

echo "=========================================="
echo "Deploying Server 1: Redis Orchestrator"
echo "=========================================="

# Check OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "Installing Redis on macOS..."
    brew install redis

    # Configure Redis to accept remote connections
    echo "Configuring Redis..."
    REDIS_CONF="/usr/local/etc/redis.conf"

    # Backup original config
    cp $REDIS_CONF ${REDIS_CONF}.backup

    # Allow external connections
    sed -i '' 's/bind 127.0.0.1/bind 0.0.0.0/' $REDIS_CONF
    sed -i '' 's/protected-mode yes/protected-mode no/' $REDIS_CONF

    # Start Redis
    echo "Starting Redis..."
    brew services start redis

elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux (Ubuntu/Debian)
    echo "Installing Redis on Linux..."
    sudo apt-get update
    sudo apt-get install -y redis-server

    # Configure Redis
    echo "Configuring Redis..."
    REDIS_CONF="/etc/redis/redis.conf"

    # Backup original config
    sudo cp $REDIS_CONF ${REDIS_CONF}.backup

    # Allow external connections
    sudo sed -i 's/bind 127.0.0.1/bind 0.0.0.0/' $REDIS_CONF
    sudo sed -i 's/protected-mode yes/protected-mode no/' $REDIS_CONF

    # Restart Redis
    echo "Starting Redis..."
    sudo systemctl restart redis-server
    sudo systemctl enable redis-server
fi

# Test Redis
echo ""
echo "Testing Redis connection..."
sleep 2
redis-cli ping

echo ""
echo "=========================================="
echo "Server 1 deployment complete!"
echo "Redis is running on port 6379"
echo ""
echo "To check status:"
echo "  redis-cli ping"
echo "  redis-cli info server"
echo "=========================================="
