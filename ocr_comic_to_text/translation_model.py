"""
Translation Module for Comic-to-Speech Pipeline
Translates English text to Dutch using OpenNMT neural machine translation

NOTE: This module wraps the original translate.py script from the model directory
to avoid compatibility issues with OpenNMT-py 3.5.1 and Python 3.12.
"""

import os
import subprocess
import tempfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── Paths ────────────────────────────────────────────────────────────────
# Look for model in the parent 'model' directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'model'))
MODEL_PATH = os.path.join(BASE_DIR, "model_step_22000.pt")
BPE_MODEL_PATH = os.path.join(BASE_DIR, "bpe.model")
TRANSLATE_SCRIPT = os.path.join(BASE_DIR, "translate.py")


# ─── Translation Function ─────────────────────────────────────────────────
def translate_text(text_or_list, src_lang="en", tgt_lang="nl"):
    """
    Translate text using the fine-tuned OpenNMT model (English to Dutch).
    Wraps the original translate.py script for compatibility.

    Args:
        text_or_list: Either a single string or a list of strings to translate
        src_lang: Source language code (default: "en")
        tgt_lang: Target language code (default: "nl" for Dutch)

    Returns:
        str or list: Translated text (same type as input)

    Raises:
        FileNotFoundError: If model files are not found
        Exception: If translation fails
    """
    # Handle both single string and list inputs
    is_single = isinstance(text_or_list, str)
    texts = [text_or_list] if is_single else text_or_list

    if not texts or (len(texts) == 1 and not texts[0].strip()):
        logger.warning("Empty text provided for translation")
        return "" if is_single else []

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model checkpoint not found: {MODEL_PATH}")
    if not os.path.exists(BPE_MODEL_PATH):
        raise FileNotFoundError(f"BPE model not found: {BPE_MODEL_PATH}")
    if not os.path.exists(TRANSLATE_SCRIPT):
        raise FileNotFoundError(f"Translation script not found: {TRANSLATE_SCRIPT}")

    logger.info(f"Translating {len(texts)} text(s) from {src_lang} to {tgt_lang}")

    # Split texts into sentences/lines for better translation
    # Each paragraph should be translated separately
    all_lines = []
    text_line_counts = []  # Track how many lines each text has

    for text in texts:
        # Split by newlines to preserve paragraph structure
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        all_lines.extend(lines)
        text_line_counts.append(len(lines))

    logger.info(f"Split {len(texts)} text(s) into {len(all_lines)} lines for translation")

    results_file = os.path.join(BASE_DIR, "results.txt")

    try:
        # Create input.txt in model directory (required by translate.py)
        model_input = os.path.join(BASE_DIR, "input.txt")
        with open(model_input, 'w', encoding='utf-8') as f:
            for line in all_lines:
                f.write(line + "\n")

        # Run the translate.py script with system Python
        # In Docker, use 'python3', otherwise try to find Python 3.11 env if available
        import sys
        python_path = sys.executable  # Use the same Python interpreter that's running this code
        logger.debug(f"Running translation script: {TRANSLATE_SCRIPT} with {python_path}")
        result = subprocess.run(
            [python_path, TRANSLATE_SCRIPT],
            cwd=BASE_DIR,  # Run in model directory
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )

        if result.returncode != 0:
            logger.error(f"Translation script failed (code {result.returncode})")
            logger.error(f"STDOUT: {result.stdout}")
            logger.error(f"STDERR: {result.stderr}")
            raise RuntimeError(f"Translation failed with code {result.returncode}: {result.stderr or result.stdout}")

        # Parse results.txt to extract translations
        if not os.path.exists(results_file):
            raise RuntimeError("Translation completed but results file not found")

        translated_lines = []
        with open(results_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Parse the format: "1. EN: ... \n   NL: ..."
            for line in lines:
                line = line.strip()
                if line.startswith("NL:"):
                    nl_text = line[3:].strip()  # Remove "NL: " prefix
                    translated_lines.append(nl_text)

        if len(translated_lines) != len(all_lines):
            logger.warning(f"Expected {len(all_lines)} translated lines, got {len(translated_lines)}")

        # Recombine lines back into original text structure
        translations = []
        line_idx = 0
        for count in text_line_counts:
            # Join the lines for this text with newlines
            text_translation = "\n\n".join(translated_lines[line_idx:line_idx + count])
            translations.append(text_translation)
            line_idx += count

        logger.info(f"Translation completed: {len(translations)} results")

        # Return same type as input
        return translations[0] if is_single else translations

    finally:
        # Cleanup is handled by translate.py
        # No additional cleanup needed
        pass


def is_translation_available():
    """
    Check if translation models are available.

    Returns:
        bool: True if models exist, False otherwise
    """
    return os.path.exists(MODEL_PATH) and os.path.exists(BPE_MODEL_PATH)


# ─── Manual test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_sentences = ["This is working!", "I love AI.", "How are you?"]
    translations = translate_text(test_sentences)

    print("\n✅ Translation results:")
    print("───────────────────────────────")
    for src, tgt in zip(test_sentences, translations):
        print(f"{src} → {tgt}")

    # Test single string
    single = translate_text("Hello world!")
    print(f"\nSingle translation: 'Hello world!' → '{single}'")
