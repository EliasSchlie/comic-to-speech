# LLM-Based Comic Narration Guide

## Overview

Your comic-to-speech application has been upgraded with OpenAI GPT-4 Vision to generate **audiobook-style narration** from comic images. The system now creates engaging narrative descriptions while preserving the original dialogue from speech bubbles.

## What Changed

### Narration Style
- **Audiobook-style narration**: Dramatic, engaging reading with context
- **Preserves original dialogue**: Extracts and includes exact text from speech bubbles
- **Adds narrative context**: Describes scenes, actions, and basic character expressions
- **Natural flow**: Creates smooth transitions between narration and dialogue

### Example Output

**Traditional OCR Output:**
```
[Panel 1]
I won't give up!
Where are you going?
```

**New LLM Narration Output:**
```
The hero stands at the edge of a crumbling building, wind whipping through their cape. They look down at the city below with determination in their eyes. "I won't give up!" they say firmly. A companion approaches from behind, concern evident in their voice. "Where are you going?" they ask, reaching out a hand.
```

## Files Modified/Created

### New Files
1. **`llm_narrator.py`** - OpenAI GPT-4 Vision integration module
2. **`.env.example`** - Environment variable template
3. **`LLM_NARRATION_GUIDE.md`** - This guide

### Modified Files
1. **`requirements.txt`** - Added `openai==1.54.0`
2. **`config.py`** - Added OpenAI API key and narrator toggle
3. **`comic_reader_fixed.py`** - Integrated LLM narrator with fallback to OCR
4. **`tasks.py`** - Updated to handle narration metadata
5. **`docker-compose.yml`** - Added OpenAI environment variables to all services
6. **`Dockerfile.interface`** - Added `llm_narrator.py` to container
7. **`Dockerfile.worker`** - Added `llm_narrator.py` to container

## How to Use

### Option 1: Docker (Recommended)

The OpenAI API key is already configured in `docker-compose.yml` with your provided key. Simply start the services:

```bash
docker-compose up --build
```

The system will automatically use LLM narration by default.

### Option 2: Local Development

1. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration (API key is already set)
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python comic_reader_fixed.py
   ```

## Configuration

### Environment Variables

- **`OPENAI_API_KEY`**: Your OpenAI API key (already configured)
- **`USE_LLM_NARRATOR`**: Enable/disable LLM narration (default: `true`)
  - Set to `false` to use traditional OCR mode
- **`REDIS_HOST`**: Redis server host (default: `localhost`)
- **`REDIS_PORT`**: Redis server port (default: `6379`)
- **`GOOGLE_APPLICATION_CREDENTIALS`**: Path to Google Cloud credentials (for TTS)

### Toggle Between OCR and LLM Modes

**To disable LLM and use traditional OCR:**

1. **Docker:** Set environment variable
   ```bash
   export USE_LLM_NARRATOR=false
   docker-compose up --build
   ```

2. **Local:** Edit `config.py` or `.env`
   ```python
   USE_LLM_NARRATOR = False
   ```

**Programmatic override:**
```python
ocr = ComicOCR()
# Force LLM mode
result = ocr.extract_text(image_bytes, use_llm=True)
# Force OCR mode
result = ocr.extract_text(image_bytes, use_llm=False)
```

## Features

### Automatic Fallback
If LLM narration fails (API error, network issue, etc.), the system automatically falls back to traditional Google Vision OCR with speech bubble detection.

### Narration Quality
The LLM is prompted to:
- Extract exact dialogue from speech bubbles
- Describe visual scenes with basic context
- Identify character actions and expressions
- Create engaging, dramatic narration suitable for text-to-speech
- Maintain story continuity across panels

### Response Metadata
Results now include additional metadata:
```python
{
    "text": "The generated narration...",
    "narration_mode": "llm",  # or "ocr"
    "tokens_used": 450,       # OpenAI tokens consumed (LLM mode only)
    "confidence": 1.0,
    "panels": [...],
    "bubbles": [...]
}
```

## Cost Considerations

### OpenAI API Pricing
- Model used: **GPT-4o** (with vision capabilities)
- Approximate cost: **~$0.005 - $0.015 per comic page** (varies by image size)
- Tokens used: Typically 300-800 tokens per page

### Cost Optimization Tips
1. **Use lower resolution images** when possible
2. **Batch process** multiple comics during off-peak hours
3. **Monitor token usage** via the `tokens_used` field in responses
4. **Set up usage alerts** in your OpenAI dashboard

## Troubleshooting

### LLM Narration Not Working

**Check logs for:**
```
⚠️ LLM narration failed: [error message]. Falling back to standard OCR.
```

**Common issues:**
1. **Invalid API key**: Verify `OPENAI_API_KEY` is correct
2. **API rate limit**: Check OpenAI dashboard for rate limits
3. **Network connectivity**: Ensure workers can reach OpenAI API
4. **Insufficient credits**: Check OpenAI account balance

**Verify configuration:**
```bash
# In Docker container
docker exec comic_ai_worker_1 env | grep OPENAI
docker exec comic_ai_worker_1 env | grep USE_LLM_NARRATOR

# Local
python -c "import config; print(f'API Key set: {bool(config.OPENAI_API_KEY)}'); print(f'LLM enabled: {config.USE_LLM_NARRATOR}')"
```

### Testing LLM Integration

Create a simple test script:
```python
from llm_narrator import get_comic_narrator
from pathlib import Path

# Test with a sample comic image
image_path = Path("test_comic.jpg")
image_bytes = image_path.read_bytes()

narrator = get_comic_narrator()
result = narrator.narrate_single_image(image_bytes)

if result['success']:
    print("✓ LLM narration working!")
    print(f"Narration: {result['narration'][:200]}...")
    print(f"Tokens used: {result['tokens_used']}")
else:
    print(f"✗ Error: {result['error']}")
```

## Architecture

### How It Works

1. **User uploads comic image** → Interface Server
2. **Job enqueued** → Redis queue
3. **Worker picks up job** → AI Worker
4. **Text extraction** → `ComicOCR.extract_text()`
   - Checks `USE_LLM_NARRATOR` config
   - If enabled: Uses `llm_narrator.py` → OpenAI GPT-4 Vision API
   - If disabled or failed: Uses Google Cloud Vision API (traditional OCR)
5. **Narration generated** → Audiobook-style text with dialogue
6. **TTS processing** → Google Cloud Text-to-Speech
7. **Audio saved** → `audio_files/` directory
8. **Result returned** → User receives audio file

### Distributed Processing

The system runs on 3 separate servers (Docker containers):
- **Redis Orchestrator** (172.25.0.10:6379) - Queue management
- **Interface Server** (172.25.0.20:5001) - Web API
- **AI Workers** (172.25.0.30-32) - LLM + OCR + TTS processing

All workers have access to the OpenAI API key and can process LLM narration tasks in parallel.

## API Response Format

### Success Response
```json
{
  "success": true,
  "extracted_text": "The hero stands tall...",
  "narration_mode": "llm",
  "tokens_used": 450,
  "confidence": 1.0,
  "panel_count": 0,
  "bubble_count": 0,
  "audio_id": "abc-123-def-456",
  "audio_url": "/api/audio/abc-123-def-456",
  "characters_used": 850
}
```

### Fallback to OCR (when LLM fails)
```json
{
  "success": true,
  "extracted_text": "[Panel 1]\nDialogue here...",
  "narration_mode": "ocr",
  "confidence": 0.95,
  "panel_count": 3,
  "bubble_count": 5,
  "audio_id": "abc-123-def-456",
  "audio_url": "/api/audio/abc-123-def-456"
}
```

## Next Steps

### To start the system:
```bash
docker-compose up --build
```

### Access the web interface:
```
http://localhost:5001
```

### Upload a comic and listen to the audiobook-style narration!

## Support

If you encounter issues:
1. Check Docker logs: `docker-compose logs -f`
2. Check worker logs: `docker logs comic_ai_worker_1`
3. Verify environment variables are set correctly
4. Ensure OpenAI API key is valid and has sufficient credits
5. Test with a simple comic image first

---

**Note**: The system is backwards compatible. You can always switch back to traditional OCR mode by setting `USE_LLM_NARRATOR=false`.
