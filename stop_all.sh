#!/bin/bash
#
# Stop all components of the distributed comic-to-speech system
#

echo "==============================================="
echo "🛑 Stopping Distributed Comic-to-Speech System"
echo "==============================================="
echo ""

# Stop Interface Server
echo "Stopping Interface Server..."
pkill -f "interface_server.py"

# Stop Workers
echo "Stopping AI Workers..."
pkill -f "start_worker.py"
pkill -f "rq worker"

# Optionally stop Redis (uncomment if you want to stop Redis too)
# echo "Stopping Redis..."
# redis-cli shutdown

echo ""
echo "✅ All components stopped"
echo ""
