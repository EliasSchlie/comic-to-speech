#!/usr/bin/env python3
"""
Task definitions for distributed comic-to-speech processing
This module contains the actual AI processing tasks that workers execute
"""

from google.cloud import texttospeech
import uuid

# Import the OCR processing logic from the original file
from comic_reader_fixed import (
    ComicOCR,
    setup_credentials,
    AUDIO_DIR,
    TEMP_DIR,
    get_tts_client
)

# Ensure credentials are set up
setup_credentials()

def process_ocr_task(image_bytes, preprocess=True):
    """
    Task: Extract text from comic image using OCR

    Args:
        image_bytes: Raw image data
        preprocess: Whether to preprocess the image

    Returns:
        dict: OCR results including text, panels, bubbles, confidence
    """
    print(f"[WORKER] Processing OCR task (preprocess={preprocess})")

    try:
        ocr = ComicOCR()
        result = ocr.extract_text(image_bytes, preprocess=preprocess)

        narration_mode = result.get('narration_mode', 'ocr')
        print(f"[WORKER] Text extraction completed using {narration_mode.upper()}: "
              f"{result['panel_count']} panels, "
              f"{result['bubble_count']} bubbles, "
              f"confidence={result['confidence']:.2f}")

        return {
            "success": True,
            "extracted_text": result["text"],
            "panel_count": result["panel_count"],
            "bubble_count": result["bubble_count"],
            "text_blocks": len(result["text_blocks"]),
            "confidence": result["confidence"],
            "narration_mode": narration_mode,
            "tokens_used": result.get("tokens_used")
        }
    except Exception as e:
        print(f"[WORKER] OCR error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def process_tts_task(text, language_code='en-US', voice_name='en-US-Neural2-F'):
    """
    Task: Generate speech audio from text using TTS

    Args:
        text: Text to convert to speech
        language_code: Language code (e.g., 'en-US')
        voice_name: Voice name (e.g., 'en-US-Neural2-F')

    Returns:
        dict: Audio file ID and metadata
    """
    print(f"[WORKER] Processing TTS task ({len(text)} chars, voice={voice_name})")

    try:
        tts_client = get_tts_client()
    except Exception as exc:
        return {
            "success": False,
            "error": f"TTS client not initialized: {exc}"
        }

    if not text:
        return {
            "success": False,
            "error": "No text provided"
        }

    try:
        # Generate audio
        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,
            pitch=0.0
        )

        response = tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        # Save audio file
        audio_id = str(uuid.uuid4())
        audio_path = AUDIO_DIR / f"{audio_id}.mp3"

        with open(audio_path, 'wb') as out:
            out.write(response.audio_content)

        print(f"[WORKER] TTS completed: audio_id={audio_id}")

        return {
            "success": True,
            "audio_id": audio_id,
            "audio_url": f"/api/audio/{audio_id}",
            "characters_used": len(text)
        }
    except Exception as e:
        print(f"[WORKER] TTS error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def process_comic_full_pipeline(image_bytes, language_code='en-US',
                                voice_name='en-US-Neural2-F', preprocess=True):
    """
    Task: Complete pipeline - OCR + TTS

    This combines both OCR and TTS into a single task.
    Useful for simpler orchestration.

    Args:
        image_bytes: Raw image data
        language_code: Language for TTS
        voice_name: Voice for TTS
        preprocess: Whether to preprocess image

    Returns:
        dict: Combined results from OCR and TTS
    """
    print(f"[WORKER] Processing full pipeline task")

    # Step 1: OCR
    ocr_result = process_ocr_task(image_bytes, preprocess)

    if not ocr_result["success"]:
        return ocr_result

    extracted_text = ocr_result["extracted_text"]

    if not extracted_text:
        return {
            "success": False,
            "error": "No text extracted from image"
        }

    # Step 2: TTS
    tts_result = process_tts_task(extracted_text, language_code, voice_name)

    if not tts_result["success"]:
        return tts_result

    # Combine results
    return {
        "success": True,
        "extracted_text": extracted_text,
        "panel_count": ocr_result["panel_count"],
        "bubble_count": ocr_result["bubble_count"],
        "text_blocks": ocr_result["text_blocks"],
        "confidence": ocr_result["confidence"],
        "narration_mode": ocr_result.get("narration_mode", "ocr"),
        "tokens_used": ocr_result.get("tokens_used"),
        "audio_id": tts_result["audio_id"],
        "audio_url": tts_result["audio_url"],
        "characters_used": tts_result["characters_used"]
    }
