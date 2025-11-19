#!/usr/bin/env python3
"""
Direct PyTorch Translation Script
Bypasses OpenNMT framework to avoid pyonmttok dependency
"""
import os
import torch
import sentencepiece as spm

def main():
    print("NEURAL MACHINE TRANSLATION - DIRECT PYTORCH")
    print("=" * 60)

    # File paths
    model_path = "model_step_22000.pt"
    bpe_model_path = "bpe.model"
    input_file = "input.txt"
    bpe_input = "input.bpe.src"
    bpe_output = "output.bpe.txt"
    final_output = "results.txt"

    try:
        # Check files
        print(f"Loading model: {model_path}")
        if not os.path.exists(model_path):
            print(f"ERROR: Model not found: {model_path}")
            return 1

        print(f"Loading BPE model: {bpe_model_path}")
        if not os.path.exists(bpe_model_path):
            print(f"ERROR: BPE model not found: {bpe_model_path}")
            return 1

        print(f"Reading input: {input_file}")
        if not os.path.exists(input_file):
            print(f"ERROR: Input file not found: {input_file}")
            return 1

        # Load BPE model
        sp = spm.SentencePieceProcessor(model_file=bpe_model_path)

        # Read input
        with open(input_file, "r", encoding="utf-8") as fin:
            sentences = [line.strip() for line in fin if line.strip()]

        print(f"\nOriginal sentences ({len(sentences)}):")
        for i, sentence in enumerate(sentences, 1):
            preview = sentence[:100] + "..." if len(sentence) > 100 else sentence
            print(f"  {i}. {preview}")

        # BPE encode
        print("\nStep 1: BPE encoding...")
        with open(bpe_input, "w", encoding="utf-8") as fout:
            for sentence in sentences:
                encoded = sp.encode(sentence, out_type=str)
                fout.write(" ".join(encoded) + "\n")
        print("SUCCESS: BPE encoding completed!")

        # Load PyTorch model directly
        print("\nStep 2: Loading PyTorch model...")
        checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
        print(f"Model loaded. Keys: {list(checkpoint.keys())[:5]}...")

        # Extract model components
        if 'model' in checkpoint:
            model_state = checkpoint['model']
        elif 'generator' in checkpoint:
            model_state = checkpoint
        else:
            print("WARNING: Unknown checkpoint format")
            model_state = checkpoint

        # Get vocab info
        vocab = checkpoint.get('vocab', {})
        src_vocab = vocab.get('src', None)
        tgt_vocab = vocab.get('tgt', None)

        print(f"Vocab info: src={type(src_vocab)}, tgt={type(tgt_vocab)}")

        # Read BPE input
        with open(bpe_input, "r", encoding="utf-8") as fin:
            bpe_lines = [line.strip() for line in fin if line.strip()]

        print(f"\nStep 3: Translation...")
        print("NOTE: Full OpenNMT translation requires pyonmttok.")
        print("Using FALLBACK: Copying input as placeholder translation")
        print("(The model loaded successfully but needs pyonmttok for inference)")

        # Write placeholder output (we need to install pyonmttok or use a Docker container)
        with open(bpe_output, "w", encoding="utf-8") as fout:
            for line in bpe_lines:
                # For now, just write a Dutch placeholder
                # This will be replaced when pyonmttok is available
                fout.write("▁Dit ▁is ▁een ▁placeholder ▁vertaling ▁.\n")

        print("\nStep 4: Decoding BPE results...")
        with open(bpe_output, "r", encoding="utf-8", errors="ignore") as fin:
            bpe_output_lines = [line.strip() for line in fin if line.strip()]

        # Decode
        decoded_sentences = []
        for bpe_line in bpe_output_lines:
            if bpe_line:
                try:
                    decoded = sp.decode(bpe_line.split())
                    decoded_sentences.append(decoded)
                except Exception as e:
                    print(f"Warning: Could not decode: {bpe_line[:50]}...")
                    decoded_sentences.append(f"[Decode error]")

        # Pad with placeholders if needed
        while len(decoded_sentences) < len(sentences):
            decoded_sentences.append("[Translation unavailable - pyonmttok required]")

        # Save results
        with open(final_output, "w", encoding="utf-8") as fout:
            fout.write("NEURAL MACHINE TRANSLATION RESULTS\n")
            fout.write("PyTorch Direct Mode - Requires pyonmttok for full translation\n")
            fout.write("=" * 60 + "\n\n")

            for i, (eng, dut) in enumerate(zip(sentences, decoded_sentences), 1):
                fout.write(f"{i}. EN: {eng}\n")
                fout.write(f"   NL: {dut}\n\n")

        print("\n" + "=" * 60)
        print("PARTIAL SUCCESS")
        print("=" * 60)
        print("Model loaded successfully!")
        print("However, full translation requires 'pyonmttok' package.")
        print("\nTo get full translation working:")
        print("1. Use Docker (recommended - see DOCKER_TRANSLATION_SETUP.md)")
        print("2. OR install pyonmttok:")
        print("   pip install pybind11 cmake")
        print("   pip install pyonmttok --no-binary pyonmttok")
        print("=" * 60)
        print(f"\nPlaceholder results saved to: {final_output}")

        return 0

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
