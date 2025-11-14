import os
import sys
import torch
import types
import warnings

# ─── Silence noisy warnings ────────────────────────────────────────────────
warnings.filterwarnings("ignore", category=FutureWarning)

# ─── Minimal mock for pyonmttok to avoid binary dependency issues ──────────
def _fake_build_vocab_from_tokens(vocab_dict):
    """Mock replacement for OpenNMT-py vocab building."""
    return vocab_dict

sys.modules["pyonmttok"] = types.SimpleNamespace(
    Tokenizer=lambda *a, **kw: None,
    build_tokenizer=lambda *a, **kw: None,
    build_vocab_from_tokens=_fake_build_vocab_from_tokens
)

# ─── Lazy import of OpenNMT ────────────────────────────────────────────────
def lazy_import_onmt():
    global build_translator, OnmtArgParser
    from onmt.translate.translator import build_translator
    from onmt.utils.parse import ArgumentParser as OnmtArgParser


# ─── Paths ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model_step_22000.pt")
BPE_MODEL_PATH = os.path.join(BASE_DIR, "bpe.model")


# ─── Translation Function ─────────────────────────────────────────────────
def translate_text(texts, src_lang="en", tgt_lang="bg"):
    """
    Translate a list of sentences using the fine-tuned OpenNMT model.
    """
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model checkpoint not found: {MODEL_PATH}")
    if not os.path.exists(BPE_MODEL_PATH):
        raise FileNotFoundError(f"BPE model not found: {BPE_MODEL_PATH}")

    lazy_import_onmt()

    # Create temp input/output files
    src_file = os.path.join(BASE_DIR, "_temp_input.txt")
    out_file = os.path.join(BASE_DIR, "_temp_output.txt")

    with open(src_file, "w", encoding="utf-8") as f:
        for line in texts:
            f.write(line.strip() + "\n")

    parser = OnmtArgParser()
    opt = parser.parse_known_args(args=[
        "-model", MODEL_PATH,
        "-src", src_file,
        "-output", out_file,
        "-replace_unk",
        "-verbose"
    ])[0]

    # ─── Compatibility fixes ───────────────────────────────────────────────
    setattr(opt, "output", out_file)
    setattr(opt, "models", [MODEL_PATH])
    setattr(opt, "gpu", -1)  # CPU mode

    # ─── Fix for PyTorch 2.6+ (safe unpickling) ────────────────────────────
    import torch.serialization, argparse
    torch.serialization.add_safe_globals([argparse.Namespace])

    # ─── Auto-fix for old checkpoint vocab format ──────────────────────────
    checkpoint = torch.load(MODEL_PATH, map_location="cpu", weights_only=False)
    if isinstance(checkpoint.get("vocab"), list):
        checkpoint["vocab"] = {"src": checkpoint["vocab"][0], "tgt": checkpoint["vocab"][1]}
        torch.save(checkpoint, MODEL_PATH)
        print("🧩 Patched vocabulary format in checkpoint.")

    # ─── Build and run translator ─────────────────────────────────────────
    translator = build_translator(opt, report_score=False)
    translator.translate(
        src_path=src_file,
        tgt_path=None,
        src_dir="",
        batch_size=32
    )

    # ─── Read output ──────────────────────────────────────────────────────
    with open(out_file, "r", encoding="utf-8") as f:
        result = [line.strip() for line in f.readlines()]

    # ─── Cleanup temp files ───────────────────────────────────────────────
    os.remove(src_file)
    os.remove(out_file)

    return result


# ─── Manual test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_sentences = ["This is working!", "I love AI.", "How are you?"]
    translations = translate_text(test_sentences)

    print("\n✅ Translation results:")
    print("───────────────────────────────")
    for src, tgt in zip(test_sentences, translations):
        print(f"{src} → {tgt}")
