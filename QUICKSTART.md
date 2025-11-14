# Quick Start Guide

## What You Need

This distributed architecture fulfills your professor's requirements:

1. ✅ **Interface Server** - Handles user requests, doesn't call AI directly
2. ✅ **AI Workers** - Contain the AI components (OCR & TTS)
3. ✅ **Queue/Orchestrator** - Uses **RQ (Redis Queue)**, a Python library for queuing

The Python library your professor mentioned is **RQ (Redis Queue)** - simple, Pythonic, and perfect for this use case!

## Installation (5 minutes)

### Step 1: Install Redis

```bash
# On macOS
brew install redis
brew services start redis

# Verify it's running
redis-cli ping
# Should respond with: PONG
```

### Step 2: Install Python Dependencies

```bash
cd /Users/selimcanmutlu/Desktop/comic-to-speech
pip install -r requirements.txt
```

### Step 3: Ensure Google Cloud Credentials

Make sure your `credentials.json` file is in the project directory.

## Running the System

### Option 1: Use the Startup Script (Easiest!)

```bash
./start_all.sh
```

This starts everything automatically:
- Redis (queue/orchestrator)
- Interface Server (port 5001)
- AI Worker (processes tasks)

### Option 2: Manual Start (for more control)

Open **3 separate terminal windows**:

**Terminal 1 - Redis:**
```bash
redis-server
```

**Terminal 2 - Interface Server:**
```bash
python3 interface_server.py
```

**Terminal 3 - AI Worker:**
```bash
python3 start_worker.py
```

**Terminal 4+ (Optional) - More Workers:**
```bash
python3 start_worker.py
```

## Using the Application

1. Open browser: http://localhost:5001
2. Upload a comic image
3. Select voice options
4. Click "Process Comic"
5. Watch the job status update in real-time!

## Stopping the System

```bash
./stop_all.sh
```

Or manually press `Ctrl+C` in each terminal.

## Architecture Summary

```
┌──────────────┐
│ Web Browser  │
└──────┬───────┘
       │
       ▼
┌─────────────────────┐
│ Interface Server    │  ← Accepts requests, enqueues jobs
│ (port 5001)         │  ← Does NOT process AI directly
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Redis Queue         │  ← Orchestrator (Python RQ library)
│ (port 6379)         │  ← Manages task distribution
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ AI Workers          │  ← Process OCR & TTS tasks
│ (multiple possible) │  ← Can run on different machines
└─────────────────────┘
```

## Why This Architecture?

### Meets Professor's Requirements

1. ✅ **Interface Server** (`interface_server.py`) - Handles user requests, validates input, stores data
2. ✅ **AI Component** (`tasks.py` + `start_worker.py`) - Separate servers containing OCR & TTS
3. ✅ **Orchestrator** (Redis + RQ) - Queue service implemented in Python (no RabbitMQ needed!)

### Benefits

- **Scalable**: Run multiple workers for parallel processing
- **Distributed**: Workers can run on different machines
- **Efficient**: Non-blocking async processing
- **Fault-tolerant**: If worker crashes, job gets re-queued
- **Simple**: Using RQ (Python library) instead of complex RabbitMQ

## Scaling Up

To handle more traffic, just start more workers:

```bash
# Worker 1
python3 start_worker.py &

# Worker 2
python3 start_worker.py &

# Worker 3
python3 start_worker.py &
```

Each worker can process one job at a time. With 3 workers, you can process 3 comics simultaneously!

## Testing the Queue System

1. Upload 3 comics at once (open 3 browser tabs)
2. Start only 1 worker
3. Watch them get processed one by one (queued → processing → completed)
4. Start more workers → see faster processing!

## Common Commands

```bash
# Check Redis is running
redis-cli ping

# Check how many jobs in queue
redis-cli
> LLEN rq:queue:default

# Check how many workers are running
> SMEMBERS rq:workers

# Clear all queues (if needed)
> FLUSHALL
```

## Files Overview

- `interface_server.py` - Web server (interface)
- `tasks.py` - Task definitions (AI functions)
- `start_worker.py` - Worker process
- `config.py` - Configuration
- `start_all.sh` - Startup script
- `stop_all.sh` - Shutdown script

## For Your Report

Your distributed system has:

1. **Interface Server**: Handles HTTP requests, enqueues tasks to Redis
2. **Orchestrator**: Redis + RQ (Python queuing library) manages task distribution
3. **AI Workers**: Process OCR and TTS tasks, can scale horizontally

The architecture is **event-driven** and **asynchronous**, allowing multiple users to submit requests simultaneously without blocking.

## Need Help?

- Check `DISTRIBUTED_ARCHITECTURE.md` for detailed architecture documentation
- Look at server logs in each terminal for debugging
- Ensure Redis is running: `redis-cli ping`

## Key Points for Your Professor

1. ✅ **Separation of concerns**: Interface doesn't call AI directly
2. ✅ **Queue-based orchestration**: Using RQ (Python library, not RabbitMQ)
3. ✅ **Scalable**: Can run multiple workers
4. ✅ **Localhost deployment**: Everything runs on one machine (can be distributed to multiple machines easily)
5. ✅ **Asynchronous processing**: Non-blocking task execution

Enjoy your distributed comic-to-speech system! 🎉
