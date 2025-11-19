#!/usr/bin/env python3
"""
Neural Machine Translation Script
English to Dutch using Step 22000 Model
"""
import os
import subprocess
import sentencepiece as spm

def main():
    print("NEURAL MACHINE TRANSLATION - STEP 22000 MODEL")
    print("=" * 60)
    
    # File paths - all in current directory
    model_path = "model_step_22000.pt"
    bpe_model_path = "bpe.model"
    input_file = "input.txt"
    bpe_input = "input.bpe.src"
    bpe_output = "output.bpe.txt"
    final_output = "results.txt"
    
    try:
        # Check if files exist
        print(f"Checking for model: {model_path}")
        if not os.path.exists(model_path):
            print(f"ERROR: Model not found: {model_path}")
            print("Current directory contents:")
            for f in os.listdir("."):
                if f.endswith(".pt"):
                    print(f"  Found model: {f}")
            return 1
            
        print(f"Checking for BPE model: {bpe_model_path}")
        if not os.path.exists(bpe_model_path):
            print(f"ERROR: BPE model not found: {bpe_model_path}")
            return 1
            
        print(f"Checking for input: {input_file}")
        if not os.path.exists(input_file):
            print(f"ERROR: Input file not found: {input_file}")
            return 1
        
        print("All files found! Starting translation...")
        
        # Load BPE model
        sp = spm.SentencePieceProcessor(model_file=bpe_model_path)
        
        # Read original input
        with open(input_file, "r", encoding="utf-8") as fin:
            sentences = [line.strip() for line in fin if line.strip()]
        
        print(f"\nOriginal sentences ({len(sentences)}):")
        for i, sentence in enumerate(sentences, 1):
            print(f"  {i}. {sentence}")
        
        print("\nStep 1: BPE encoding...")
        # Encode input with BPE
        with open(bpe_input, "w", encoding="utf-8") as fout:
            for sentence in sentences:
                encoded = sp.encode(sentence, out_type=str)
                fout.write(" ".join(encoded) + "\n")
        print("SUCCESS: BPE encoding completed!")
        
        print("\nStep 2: Running translation...")
        # Run OpenNMT translation - use onmt_translate from PATH (works in Docker and locally)
        onmt_translate = "onmt_translate"
        cmd = [
            onmt_translate,
            "-model", model_path,
            "-src", bpe_input,
            "-output", bpe_output,
            "-replace_unk",
            "-gpu", "-1"
        ]

        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"ERROR: Translation failed!")
            print(f"Error output: {result.stderr}")
            return 1
        
        print("SUCCESS: Translation completed!")
        
        print("\nStep 3: Decoding BPE results...")
        # Read BPE output
        with open(bpe_output, "r", encoding="utf-8", errors="ignore") as fin:
            bpe_lines = [line.strip() for line in fin if line.strip()]
        
        print(f"Found {len(bpe_lines)} translated lines")
        
        # Decode BPE to get final translations
        decoded_sentences = []
        for bpe_line in bpe_lines:
            if bpe_line:
                try:
                    decoded = sp.decode(bpe_line.split())
                    decoded_sentences.append(decoded)
                except Exception as e:
                    print(f"Warning: Could not decode line: {bpe_line[:50]}...")
                    decoded_sentences.append(f"[Decode error: {str(e)}]")
        
        # Save results
        with open(final_output, "w", encoding="utf-8") as fout:
            fout.write("NEURAL MACHINE TRANSLATION RESULTS\n")
            fout.write("Step 22000 Model - OpenNMT-py 3.5.1 + PyTorch 2.2.2\n")
            fout.write("=" * 60 + "\n\n")
            
            for i, (eng, dut) in enumerate(zip(sentences, decoded_sentences), 1):
                fout.write(f"{i}. EN: {eng}\n")
                fout.write(f"   NL: {dut}\n\n")
        
        # Display results
        print("\n" + "=" * 60)
        print("TRANSLATION RESULTS - SUCCESS!")
        print("=" * 60)
        
        for i, (eng, dut) in enumerate(zip(sentences, decoded_sentences), 1):
            print(f"{i}. EN: {eng}")
            print(f"   NL: {dut}")
            print()
        
        print("=" * 60)
        print("SUCCESS! Neural Machine Translation completed!")
        print(f"Results saved to: {final_output}")
        print("Your Step 22000 model is working perfectly!")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
