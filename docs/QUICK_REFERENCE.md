# Korean Forced Aligner - Quick Reference

## Installation

```bash
git clone https://github.com/exphon/kfaligner.git
cd kfaligner
pip install -r requirements.txt
pip install -e .
```

**Note**: HTK must be installed separately from http://htk.eng.cam.ac.uk/

## Common Commands

### 1. Convert Korean Text to Phonemes

```python
from kfaligner.korean_phonemes import hangul_to_phonemes

text = "안녕하세요"
phonemes = hangul_to_phonemes(text)
# Result: ['a', 'n_f', 'n', 'yeo', 'ng_f', 'h', 'a', 's', 'e', 'yo']
```

### 2. Prepare Training Data

```bash
python scripts/prepare_data.py data/sample_text.txt output/data
```

Output files:
- `output/data/dict.txt` - Pronunciation dictionary
- `output/data/phonemes.txt` - List of all phonemes
- `output/data/transcriptions.txt` - Phoneme transcriptions

### 3. Initialize Models

```bash
python scripts/train_models.py output/data output/models
```

### 4. Perform Forced Alignment

```python
from kfaligner import KoreanForcedAligner
from kfaligner.korean_phonemes import hangul_to_phonemes

aligner = KoreanForcedAligner(
    model_dir="output/models",
    config_dir="config"
)

text = "안녕하세요"
phonemes = hangul_to_phonemes(text)

result = aligner.align(
    audio_file="audio.wav",
    transcription=phonemes,
    output_dir="output/alignment"
)

# Parse results
if result:
    alignments = aligner.parse_alignment(result)
    for file_id, segments in alignments.items():
        for start, end, label in segments:
            start_sec = start / 10000000
            end_sec = end / 10000000
            print(f"{start_sec:.3f}s - {end_sec:.3f}s: {label}")
```

### 5. Batch Processing

```python
audio_files = ["audio1.wav", "audio2.wav", "audio3.wav"]
texts = ["안녕하세요", "감사합니다", "좋은 하루"]

transcriptions = [hangul_to_phonemes(text) for text in texts]
results = aligner.align_batch(audio_files, transcriptions, "output/batch")
```

## Korean Phoneme Set

### Consonants (18)
`g, gg, n, d, dd, r, m, b, bb, s, ss, j, jj, ch, k, t, p, h`

### Vowels (21)
`a, ae, ya, yae, eo, e, yeo, ye, o, wa, wae, oe, yo, u, wo, we, wi, yu, eu, ui, i`

### Final Consonants (7)
`k_f, n_f, t_f, l_f, m_f, p_f, ng_f`

### Special (2)
`sil` (silence), `sp` (short pause)

## HTK Tools Used

- **HCopy**: Extract MFCC features from audio
- **HVite**: Perform forced alignment
- **HERest**: Train HMM models
- **HCompV**: Initialize model parameters

## File Structure

```
kfaligner/
├── kfaligner/           # Main package
│   ├── aligner.py       # Core aligner
│   └── korean_phonemes.py  # Phoneme utilities
├── config/              # HTK configurations
├── scripts/             # Utility scripts
├── data/                # Sample data
├── docs/                # Documentation
└── setup.py            # Package setup
```

## Example Workflow

1. **Prepare your data**:
   - Korean text file (one utterance per line)
   - Corresponding WAV audio files

2. **Create dictionary and phoneme list**:
   ```bash
   python scripts/prepare_data.py your_text.txt output/data
   ```

3. **Extract features from audio**:
   ```bash
   HCopy -C config/config.mfcc audio.wav features.mfc
   ```

4. **Initialize models**:
   ```bash
   python scripts/train_models.py output/data output/models
   ```

5. **Train models** (with your training data):
   ```bash
   HERest -C config/config.train -I train.mlf -S train.scp \
          -H output/models/hmmdefs -M output/models \
          output/models/models.list
   ```

6. **Perform alignment**:
   ```python
   from kfaligner import KoreanForcedAligner
   aligner = KoreanForcedAligner(model_dir="output/models")
   result = aligner.align("audio.wav", phonemes, "output/alignment")
   ```

## Troubleshooting

**Issue**: HTK tools not found  
**Solution**: Ensure HTK is installed and in your PATH

**Issue**: Feature extraction fails  
**Solution**: Check audio format (must be WAV, 16-bit PCM recommended)

**Issue**: Alignment produces poor results  
**Solution**: Train models with more data, or adjust beam width in config

## Resources

- [README.md](../README.md) - Full documentation
- [HTK_INTEGRATION.md](HTK_INTEGRATION.md) - HTK integration details
- [HTK Book](http://htk.eng.cam.ac.uk/docs/docs.shtml) - Official HTK documentation

## License

MIT License - See [LICENSE](../LICENSE) for details
