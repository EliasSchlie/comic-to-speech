#!/bin/bash
#
# Start all components of the distributed comic-to-speech system
#
# This script starts:
# 1. Redis (queue/orchestrator)
# 2. Interface Server (web UI)
# 3. Worker(s) (AI processing)
#

echo "==============================================="
echo "🚀 Starting Distributed Comic-to-Speech System"
echo "==============================================="
echo ""

# Check if Redis is installed
if ! command -v redis-server &> /dev/null; then
    echo "❌ Redis is not installed!"
    echo "   Install it with: brew install redis"
    exit 1
fi

# Start Redis if not already running
if ! pgrep -x "redis-server" > /dev/null; then
    echo "📊 Starting Redis (Queue/Orchestrator)..."
    redis-server --daemonize yes
    sleep 2
    echo "✓ Redis started"
else
    echo "✓ Redis is already running"
fi

# Start Interface Server in background
echo ""
echo "🌐 Starting Interface Server (port 5001)..."
python3 interface_server.py &
INTERFACE_PID=$!
echo "✓ Interface Server started (PID: $INTERFACE_PID)"

# Wait a bit for server to start
sleep 3

# Start Workers (you can increase the number of workers for scalability)
echo ""
echo "🤖 Starting AI Workers..."
python3 start_worker.py &
WORKER1_PID=$!
echo "✓ Worker 1 started (PID: $WORKER1_PID)"

# Uncomment to start more workers:
# python3 start_worker.py &
# WORKER2_PID=$!
# echo "✓ Worker 2 started (PID: $WORKER2_PID)"

# python3 start_worker.py &
# WORKER3_PID=$!
# echo "✓ Worker 3 started (PID: $WORKER3_PID)"

echo ""
echo "==============================================="
echo "✅ All components started successfully!"
echo "==============================================="
echo ""
echo "📍 Web Interface: http://localhost:5001"
echo ""
echo "Architecture:"
echo "  1. Interface Server (port 5001) - Handles user requests"
echo "  2. Redis (port 6379) - Queue/Orchestrator"
echo "  3. Workers ($WORKER1_PID) - AI Processing"
echo ""
echo "To stop all components, run: ./stop_all.sh"
echo "Or press Ctrl+C and run: ./stop_all.sh"
echo ""
echo "Logs will appear below:"
echo "==============================================="
echo ""

# Wait for all background processes
wait
