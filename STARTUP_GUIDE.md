# Comic-to-Speech Startup Guide

## Overview
Your system uses a distributed architecture with:
- **Redis** (Queue/Orchestrator)
- **Interface Server** (Web UI)
- **AI Workers** (Process OCR/TTS tasks)

## Prerequisites
- Docker & Docker Compose installed
- OpenAI API key configured in `.env`
- Google Cloud credentials in `credentials.json` (for TTS only)

---

## Option 1: Docker (Recommended - Fully Distributed)

### Start Everything with One Command:
```bash
docker-compose up --build
```

This will start:
- ✅ Redis server (orchestrator)
- ✅ Interface server on http://localhost:5001
- ✅ 3 AI workers (scalable)

### Start with Specific Number of Workers:
```bash
# Start with just 1 worker
docker-compose up --build redis interface worker1

# Start with 2 workers
docker-compose up --build redis interface worker1 worker2
```

### Run in Background (Detached Mode):
```bash
docker-compose up -d --build
```

### View Logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f worker1
docker-compose logs -f interface
```

### Stop Everything:
```bash
docker-compose down
```

### Rebuild After Code Changes:
```bash
docker-compose down
docker-compose up --build
```

---

## Option 2: Local Development (Without Docker)

### Step 1: Start Redis
```bash
# Check if Redis is running
redis-cli ping

# If not running, start it:
brew services start redis
```

### Step 2: Start Interface Server
Open a terminal and run:
```bash
cd /Users/selimcanmutlu/Desktop/comic-to-speech
python interface_server.py
```

The interface will be available at: http://localhost:5001

### Step 3: Start Workers
Open **separate terminals** for each worker:

**Terminal 1 (Worker 1):**
```bash
cd /Users/selimcanmutlu/Desktop/comic-to-speech
python start_worker.py
```

**Terminal 2 (Worker 2) - Optional:**
```bash
cd /Users/selimcanmutlu/Desktop/comic-to-speech
python start_worker.py
```

**Terminal 3 (Worker 3) - Optional:**
```bash
cd /Users/selimcanmutlu/Desktop/comic-to-speech
python start_worker.py
```

### Stop Local Development:
- Press `Ctrl+C` in each terminal to stop the processes
- Stop Redis: `brew services stop redis`

---

## Quick Start Commands

### Docker (Production-like):
```bash
# Start everything
docker-compose up --build

# Access at: http://localhost:5001
```

### Local (Development):
```bash
# Terminal 1: Start Redis (if not running)
brew services start redis

# Terminal 2: Start Interface
python interface_server.py

# Terminal 3: Start Worker
python start_worker.py
```

---

## Troubleshooting

### Issue: "Jobs stuck in QUEUED status"
**Solution:** Make sure at least one worker is running
```bash
# For Docker:
docker-compose logs worker1

# For Local:
# Check if start_worker.py is running
```

### Issue: "Redis connection failed"
**Solution:**
```bash
# Check Redis is running
redis-cli ping

# Start Redis
brew services start redis

# For Docker, Redis should start automatically
docker-compose up redis
```

### Issue: "OpenAI API error"
**Solution:** Check your `.env` file has the correct API key:
```bash
cat .env | grep OPENAI_API_KEY
```

### Issue: "Google Cloud TTS error"
**Solution:** Ensure `credentials.json` exists:
```bash
ls -la credentials.json
```

---

## Architecture Diagram

```
┌─────────────────┐
│   Web Browser   │
│  localhost:5001 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Interface Server│ ◄──┐
│   (Flask App)   │    │
└────────┬────────┘    │
         │             │
         ▼             │
┌─────────────────┐    │
│  Redis Queue    │    │
│  (Orchestrator) │    │
└────────┬────────┘    │
         │             │
    ┌────┴────┬────────┤
    ▼         ▼        ▼
┌────────┐ ┌────────┐ ┌────────┐
│Worker 1│ │Worker 2│ │Worker 3│
│  (AI)  │ │  (AI)  │ │  (AI)  │
└────────┘ └────────┘ └────────┘
   │
   ├─ ChatGPT Vision (Text Extraction)
   └─ Google TTS (Audio Generation)
```

---

## System Features

✅ **ChatGPT Vision** - Extracts text from comics with narrative style
✅ **Distributed Processing** - Multiple workers handle requests in parallel
✅ **Queue Management** - Redis manages task distribution
✅ **Scalable** - Add more workers as needed
✅ **Fault Tolerant** - Failed tasks can be retried
✅ **Audiobook Style** - Narrative descriptions + dialogue

---

## Configuration

### Environment Variables (.env)
```bash
OPENAI_API_KEY=your-key-here
USE_LLM_NARRATOR=true
REDIS_HOST=localhost
REDIS_PORT=6379
GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
```

### Toggle Between OCR and LLM
Edit `.env`:
```bash
# Use ChatGPT Vision (recommended)
USE_LLM_NARRATOR=true

# Use Google OCR (fallback)
USE_LLM_NARRATOR=false
```

---

## Performance Tips

1. **More Workers = Faster Processing**
   - Start multiple workers for parallel processing
   - Docker: Use `docker-compose up --scale worker1=5`

2. **Monitor Queue**
   ```bash
   # Check queue status
   redis-cli LLEN rq:queue:default
   ```

3. **Clear Queue (if needed)**
   ```bash
   redis-cli FLUSHALL
   ```

---

## Next Steps

1. Start the system using either Docker or Local method
2. Open http://localhost:5001 in your browser
3. Upload a comic page
4. Watch it process through the distributed system!

For issues or questions, check the logs first:
- Docker: `docker-compose logs -f`
- Local: Check terminal outputs
