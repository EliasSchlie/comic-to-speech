# Comic-to-Speech 🎭📚🔊

AI-powered comic book narration system that transforms visual comics into immersive audiobook experiences using GPT-4 Vision, Google Cloud TTS, and Neural Machine Translation.

## Features

- **🎭 Cinematic Narration**: GPT-4 Vision creates audiobook-style narration with dialogue and scene descriptions.
- **🌐 Neural Translation**: Optional English to Dutch translation using a fine-tuned OpenNMT Transformer.
- **🔊 Text-to-Speech**: High-quality Google Cloud TTS with multiple character voices.
- **⚡ Distributed Architecture**: Redis-based task queue with parallel AI workers.
- **🐳 Docker Ready**: Full containerized setup for easy deployment.

## Architecture

```mermaid
graph TD
    User[User / Web UI] -->|Upload| Interface[Interface Server]
    Interface -->|Enqueue Task| Redis[Redis Queue]
    Redis -->|Distribute| Worker1[AI Worker 1]
    Redis -->|Distribute| Worker2[AI Worker 2]
    Redis -->|Distribute| Worker3[AI Worker 3]
    
    subgraph Worker Processing
        Worker1 -->|1. Extract/Narrate| GPT[GPT-4 Vision / OCR]
        Worker1 -->|2. Translate (Opt)| NMT[OpenNMT Model]
        Worker1 -->|3. Synthesize| TTS[Google Cloud TTS]
    end
```

## Quick Start

### Prerequisites
- **Docker** & **Docker Compose**
- **OpenAI API Key** (for GPT-4 Vision)
- **Google Cloud Credentials** (JSON file for Vision/TTS)

### 1. Setup
```bash
git clone https://github.com/EliasSchlie/comic-to-speech
cd comic-to-speech

# Setup credentials
cp path/to/your/credentials.json credentials.json

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Translation Model (Important)
The translation model (~1GB) is not in the repo. 
1. Download from [Google Drive](https://drive.google.com/file/d/1yEbxA-JgA2Dq-uELBoZITTPT0o3pKXBy/view?usp=share_link).
2. Extract contents directly into `model/` folder.
   - Structure should be: `model/model_step_22000.pt`, `model/bpe.model`, etc.

### 3. Run with Docker (Recommended)
This starts the Redis orchestrator, Interface server, and AI Workers.

```bash
docker-compose up --build -d
```

Access the web interface at **http://localhost:5001**.

### Managing Services

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up --build -d
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Required for LLM narration | - |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to GCP JSON key | `credentials.json` |
| `USE_LLM_NARRATOR` | `true` for GPT-4, `false` for OCR only | `true` |
| `REDIS_HOST` | Redis hostname | `localhost` |

## Project Structure

### Core Application Files

| File | Purpose |
|------|---------|
| `interface_server.py` | Flask web server with UI and API. Handles user uploads and enqueues jobs to Redis. |
| `start_worker.py` | Worker process that consumes tasks from Redis queue and executes AI pipelines. |
| `tasks.py` | Defines async task functions: OCR/narration, translation, and TTS synthesis. |
| `config.py` | Central configuration loading environment variables and defaults. |

### AI Processing Modules

| File / Folder | Purpose |
|---------------|---------|
| `llm_narrator.py` | GPT-4 Vision integration for cinematic comic narration. |
| `comic_reader_fixed.py` | Fallback OCR using Google Cloud Vision API. |
| `ocr_comic_to_text/` | Legacy OCR logic & Neural machine translation module (EN→NL) using OpenNMT. |

### Infrastructure

| File / Folder | Purpose |
|---------------|---------|
| `docker-compose.yml` | Orchestrates Redis, Interface Server, and 3 AI Workers. |
| `Dockerfile.interface` | Container definition for the web interface server. |
| `Dockerfile.worker` | Container definition for AI worker processes. |
| `requirements.txt` | Python dependencies for the entire system. |

### Data & Assets

| Folder | Purpose |
|--------|---------|
| `model/` | OpenNMT translation model weights (~1GB, gitignored, download separately). |
| `audio_files/` | Generated audio outputs (MP3 files). |
| `temp_images/` | Temporary storage for uploaded images during processing. |
| `comics/` | Example comic images for testing. |
| `tests/` | Unit and integration test suites. |

## Troubleshooting

- **Services won't start**: Check `docker-compose logs`. Ensure `model/` folder is populated if building workers.
- **No Audio**: Verify GCP credentials and TTS API enablement.
- **Queue Stuck**: Check Redis connection (`docker logs comic_redis_orchestrator`).

## License
Educational purpose only.
