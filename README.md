# Comic-to-Speech 🎭📚🔊

AI-powered comic book narration system that transforms visual comics into immersive audiobook experiences using GPT-4 Vision, Google Cloud TTS, and Neural Machine Translation.

## Features

- **🎭 Cinematic Narration**: GPT-4 Vision creates audiobook-style narration with dialogue and scene descriptions.
- **🌐 Neural Translation**: Optional English to Dutch translation using a fine-tuned OpenNMT Transformer.
- **🔊 Text-to-Speech**: High-quality Google Cloud TTS with multiple character voices.
- **⚡ Distributed Architecture**: Redis-based task queue with parallel AI workers.
- **🐳 Docker Ready**: Full containerized setup for easy deployment.

## Demo

[![Demo Video](https://img.youtube.com/vi/7g8XIVirimQ/0.jpg)](https://youtu.be/7g8XIVirimQ)

Watch the system in action: [Comic-to-Speech Demo](https://youtu.be/7g8XIVirimQ)

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
cd docker
docker-compose up --build -d
```

Access the web interface at **http://localhost:5001**.

### Managing Services

```bash
# View logs (from docker/ directory)
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

> **📝 Note**: All main Python files contain detailed docstrings explaining their purpose, architecture role, and key functions. Use `help(module_name)` or read the module headers for comprehensive documentation.

### Core Application Modules

| Module | Purpose |
|--------|---------|
| `server/` | **Web Interface** - Flask server with UI and API endpoints. Handles uploads and job queuing. |
| `workers/` | **Task Processing** - Worker processes and task definitions for distributed AI execution. |
| `narration/` | **Text Extraction** - LLM-based narration (GPT-4 Vision) and OCR fallback (Google Vision). |
| `translation/` | **Language Translation** - Neural machine translation (EN→NL) using OpenNMT. |
| `ocr/` | **Advanced OCR** - Speech bubble detection and panel ordering utilities. |
| `config.py` | **Central Configuration** - Environment variables and system defaults. |

### Key Files

| File | Purpose |
|------|---------|
| `server/interface_server.py` | Flask web server that enqueues jobs to Redis queue. |
| `workers/worker.py` | Worker entry point that consumes and executes tasks from Redis. |
| `workers/tasks.py` | Task function definitions (OCR, translation, TTS, full pipeline). |
| `narration/llm_narrator.py` | GPT-4 Vision integration for cinematic narration. |
| `narration/vision_ocr.py` | Google Cloud Vision OCR fallback. |
| `translation/translator.py` | OpenNMT-based translation module (EN→NL). |

### Infrastructure

| File / Folder | Purpose |
|---------------|---------|
| `docker/` | **Docker Configuration** - All containerization files. |
| `docker/docker-compose.yml` | Orchestrates Redis, Interface Server, and 3 AI Workers. |
| `docker/Dockerfile.interface` | Container definition for the web interface server. |
| `docker/Dockerfile.worker` | Container definition for AI worker processes. |
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
