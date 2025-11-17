# Comic-to-Speech

AI-powered comic book narration system that transforms visual comics into immersive audiobook experiences. Uses OpenAI GPT-4 Vision for cinematic narration, Google Cloud Vision for OCR fallback, neural machine translation (EN→NL), and Google Cloud TTS for natural-sounding speech.

## Features

- **🎭 Cinematic LLM Narration** - GPT-4 Vision creates audiobook-style narration with dialogue and scene descriptions
- **👁️ OCR Fallback** - Google Cloud Vision API for traditional text extraction with speech bubble detection
- **🌐 Neural Translation** - English to Dutch translation using fine-tuned OpenNMT Transformer (93M parameters)
- **🔊 Text-to-Speech** - Google Cloud TTS with multiple voices (English & Dutch)
- **⚡ Distributed Processing** - Redis-based task queue with 3 parallel AI workers
- **🐳 Docker Deployment** - Full containerized setup for easy deployment
- **🌐 Web Interface** - Simple drag-and-drop UI for comic upload and processing

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Google Cloud credentials (for Vision API & TTS)
- OpenAI API key (for LLM narration)

### 1. Setup Environment

```bash
# Clone the repository
git clone https://github.com/EliasSchlie/comic-to-speech
cd comic-to-speech

# Create credentials file
cp path/to/your/credentials.json credentials.json

# Configure environment (optional - defaults work)
cp .env.example .env
```

### 2. Start Services

```bash
docker-compose up --build -d
```

This starts:
- **Redis Orchestrator** (queue management)
- **Interface Server** (web UI on port 5001)
- **3 AI Workers** (parallel processing)

### 3. Access the App

Open in your browser: **http://localhost:5001**

### 4. Process a Comic

1. Upload a comic image (drag & drop or click)
2. Select narration mode:
   - **LLM Narration** (default) - Audiobook-style with GPT-4 Vision
   - **OCR Mode** - Traditional text extraction
3. Optional: Enable Dutch translation
4. Select TTS voice
5. Click "Process Comic"
6. Listen to the generated audio!

## Architecture

```
Comic Image Upload
      ↓
 Interface Server (Flask API)
      ↓
  Redis Queue
      ↓
AI Workers (3 parallel workers)
      ↓
┌─────────────────────┐
│ 1. Text Extraction  │
│   - LLM (GPT-4V) OR │
│   - OCR (GCP Vision)│
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ 2. Translation      │
│   (Optional EN→NL)  │
│   - OpenNMT Model   │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ 3. Text-to-Speech   │
│   - Google Cloud TTS│
└──────────┬──────────┘
           ↓
    Audio Output (MP3)
```

## Configuration

### Environment Variables

Set in `.env` file or `docker-compose.yml`:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4 Vision | Required for LLM mode |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to GCP credentials | `credentials.json` |
| `USE_LLM_NARRATOR` | Enable LLM narration | `true` |
| `REDIS_HOST` | Redis server hostname | `localhost` |
| `REDIS_PORT` | Redis server port | `6379` |

### Translation

The translation model files (`model/` directory, ~1.1GB) are **NOT** included in the repository due to size.

**Download the pre-trained model (recommended)**
1. Download the archive from Google Drive: https://drive.google.com/file/d/1yEbxA-JgA2Dq-uELBoZITTPT0o3pKXBy/view?usp=share_link
2. Unzip the download and copy the contents into the repo’s `model/` folder so the files sit directly inside `model/` (not in a nested subfolder).
   - You should end up with `model/model_step_22000.pt`, `model/bpe.model`, `model/translate.py`, etc.
3. If you use Docker, download/extract the model before running `docker-compose build` so the worker image bundles the files.

**Alternative:** train your own OpenNMT model and place the resulting files in `model/` with the same names:
- `model_step_22000.pt` - Translation checkpoint
- `bpe.model` - SentencePiece tokenizer

Translation is optional and gracefully degrades if model files are missing.

## Docker Services

| Service | Port | Role |
|---------|------|------|
| `redis` | 6379 | Task queue orchestrator |
| `interface` | 5001 | Web UI & API |
| `worker1-3` | - | AI processing (LLM/OCR/TTS) |

### Managing Services

```bash
# View status
docker-compose ps

# View logs
docker-compose logs -f

# View specific service logs
docker logs comic_ai_worker_1

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose build
docker-compose up -d
```

## API Endpoints

### Health Check
```bash
GET /api/health
```

### Process Comic (Full Pipeline)
```bash
POST /api/process
Content-Type: multipart/form-data

{
  "image": <file>,
  "translate": "true|false",
  "language": "en-US|nl-NL",
  "voice": "en-US-Neural2-F|nl-NL-Standard-A|..."
}
```

### Get Audio File
```bash
GET /api/audio/<audio_id>
```

## LLM Narration vs OCR Mode

### LLM Narration (Default)
- **Model**: OpenAI GPT-4o with Vision
- **Output**: Cinematic audiobook-style narration
- **Features**: Scene descriptions, character emotions, dialogue context
- **Cost**: ~$0.005-$0.015 per page
- **Speed**: 2-5 seconds per page

### OCR Mode (Fallback)
- **Model**: Google Cloud Vision API
- **Output**: Raw text extraction
- **Features**: Panel detection, speech bubble recognition
- **Cost**: Free tier available
- **Speed**: 1-2 seconds per page

Toggle between modes:
```bash
# Disable LLM, use OCR only
export USE_LLM_NARRATOR=false
docker-compose up --build
```

## Translation Feature

### Supported Languages
- **English → Dutch (Nederlands)**

### Available Dutch Voices
- `nl-NL-Standard-A` - Female (Standard)
- `nl-NL-Standard-B` - Male (Standard)
- `nl-NL-Wavenet-A` - Female (Premium)
- `nl-NL-Wavenet-B` - Male (Premium)

### Translation Model Details
- **Architecture**: Transformer (6 layers)
- **Parameters**: 93.3 million
- **Training**: 22,000 steps
- **Tokenization**: SentencePiece BPE (32K vocab)
- **Performance**: First run ~5-10s (model load), subsequent <1s

## Development

### Local Setup (Without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-key"
export GOOGLE_APPLICATION_CREDENTIALS="credentials.json"

# Start Redis (requires Redis installed)
redis-server

# Start interface server
python interface_server.py

# Start workers (in separate terminals)
python start_worker.py
```

### Running Tests

```bash
# Translation integration test
python test_translation_integration.py

# Full pipeline test
python tests/test_integration_pipeline.py
```

## Project Structure

```
comic-to-speech/
├── interface_server.py          # Flask web UI & API
├── start_worker.py             # Redis queue worker
├── tasks.py                    # Task definitions (OCR/TTS/Translation)
├── comic_reader_fixed.py       # Core OCR logic
├── llm_narrator.py             # OpenAI GPT-4 Vision integration
├── config.py                   # Configuration
├── requirements.txt            # Python dependencies
├── docker-compose.yml          # Docker orchestration
├── Dockerfile.interface        # Interface container
├── Dockerfile.worker           # Worker container
├── ocr_comic_to_text/
│   └── translation_model.py    # OpenNMT translation wrapper
├── audio_files/                # Generated audio (gitignored)
├── temp_images/                # Temporary uploads (gitignored)
├── model/                      # Translation model (gitignored, 1GB+)
└── tests/                      # Test suites
```

## Troubleshooting

### Services Won't Start
```bash
# Check logs
docker-compose logs

# Clean restart
docker-compose down
docker-compose up --build -d
```

### LLM Narration Not Working
- Verify `OPENAI_API_KEY` is set correctly
- Check OpenAI account credits/limits
- View worker logs: `docker logs comic_ai_worker_1`
- System automatically falls back to OCR on error

### Translation Fails
- Check if `model/` directory exists with model files
- First translation takes 5-10s (model loading)
- View logs: `docker logs comic_ai_worker_1 | grep -i translation`

### No Audio Generated
- Verify Google Cloud credentials are valid
- Check GCP project has TTS API enabled
- Ensure sufficient GCP credits

### Job Stuck in Queue
```bash
# Check Redis connection
docker logs comic_redis_orchestrator

# Restart workers
docker-compose restart worker1 worker2 worker3
```

## Performance & Costs

### Processing Time (per comic page)
- LLM Narration: 2-5 seconds
- OCR Mode: 1-2 seconds
- Translation: <1 second (after initial load)
- TTS: 1-2 seconds
- **Total**: 4-10 seconds per page

### API Costs (approximate)
- OpenAI GPT-4 Vision: $0.005-$0.015 per page
- Google Cloud Vision OCR: Free tier available
- Google Cloud TTS: ~$0.000016 per character
- Translation: Local model (no API cost)

### Resource Requirements
- **RAM**: ~2GB per worker (when translation model loaded)
- **Disk**: ~1.5GB (including translation model)
- **Network**: Outbound API calls to OpenAI & Google Cloud

## License

This project is provided as-is for educational purposes. Translation model files may have separate licensing terms.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues or questions:
1. Check Docker logs: `docker-compose logs -f`
2. Verify environment variables are set
3. Test with a simple comic image first
4. Check API keys and credits

---

**Ready to transform comics into audiobooks!** 🎭📚🔊

