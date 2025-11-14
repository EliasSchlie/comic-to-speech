# Neural Machine Translation

## English to Dutch Translation Model

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Environment

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install "OpenNMT-py==3.5.1"
pip install "torch==2.2.2"
pip install sentencepiece
```

### 4. Verify Installation

```bash
python -c "import onmt; print('OpenNMT-py installed successfully')"
python -c "import torch; print(f'PyTorch {torch.__version__} installed')"
```

## Files

- `translate.py` - Main translation script
- `input.txt` - Your English sentences to translate
- `results.txt` - Translation results (generated after running)
- `model_step_22000.pt` - Your trained model (1.1GB)
- `bpe.model` - Subword tokenizer
- `model_env/` - Python environment with dependencies
- `SE4CSAI_2025_Practical/` - Training data and configuration

## How It Works

1. **Input**: English sentences from `input.txt`
2. **Encoding**: Converts words to subword tokens using BPE
3. **Translation**: Neural model translates English → Dutch
4. **Decoding**: Converts tokens back to Dutch text
5. **Output**: Results saved to `results.txt`

## Technical Details

- **Model**: 6-layer Transformer (93.3M parameters)
- **Training**: 22,000 steps, 57.99% validation accuracy
- **Architecture**: Encoder-decoder with attention
- **Vocabulary**: 32,008 BPE subword tokens

## Environment

- OpenNMT-py 3.5.1
- PyTorch 2.2.2
- SentencePiece (BPE processing)

**Ready to translate! Just run `python translate.py`** 🚀
