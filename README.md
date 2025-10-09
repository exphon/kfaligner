# kfaligner
Korean forced aligner using HTK (Hidden Markov Model Toolkit)

## Overview

kfaligner is an HTK-based forced alignment system for Korean speech. It automatically aligns Korean phonetic transcriptions with audio recordings, providing time-stamped phoneme boundaries.

## Features

- **HTK Integration**: Uses the proven Hidden Markov Model Toolkit for acoustic modeling
- **Korean Phoneme Support**: Comprehensive Korean phoneme set including initial, medial, and final consonants
- **Automatic Text Processing**: Converts Korean Hangul text to phoneme sequences
- **Batch Processing**: Support for aligning multiple audio files
- **Configurable**: Customizable HTK configuration for different use cases

## Requirements

- Python 3.6+
- HTK Toolkit (must be installed separately)
  - Download from: http://htk.eng.cam.ac.uk/
  - Follow HTK installation instructions for your platform

## Installation

1. Install HTK toolkit (required for forced alignment)

2. Clone this repository:
```bash
git clone https://github.com/exphon/kfaligner.git
cd kfaligner
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Install the package:
```bash
pip install -e .
```

## Quick Start

### 1. Prepare Training Data

Convert Korean text to phonemes and create pronunciation dictionary:

```bash
python scripts/prepare_data.py data/sample_text.txt output/prepared_data
```

### 2. Initialize and Train Models

Initialize HMM models for Korean phonemes:

```bash
python scripts/train_models.py output/prepared_data output/models
```

### 3. Perform Forced Alignment

```python
from kfaligner import KoreanForcedAligner
from kfaligner.korean_phonemes import hangul_to_phonemes

# Initialize aligner
aligner = KoreanForcedAligner(
    model_dir="output/models",
    config_dir="config"
)

# Convert Korean text to phonemes
text = "안녕하세요"
phonemes = hangul_to_phonemes(text)

# Align audio with phonemes
result = aligner.align(
    audio_file="audio.wav",
    transcription=phonemes,
    output_dir="output/alignment"
)

# Parse alignment results
if result:
    alignments = aligner.parse_alignment(result)
    for file_id, segments in alignments.items():
        for start, end, label in segments:
            print(f"{start/10000000:.3f}s - {end/10000000:.3f}s: {label}")
```

## Usage Examples

### Example 1: Korean Text to Phonemes

```python
from kfaligner.korean_phonemes import hangul_to_phonemes

text = "안녕하세요"
phonemes = hangul_to_phonemes(text)
print(phonemes)  # ['n', 'yeo', 'ng_f', 'h', 'a', 'se', 'yo']
```

### Example 2: Batch Processing

```python
from kfaligner import KoreanForcedAligner

aligner = KoreanForcedAligner()

audio_files = ["audio1.wav", "audio2.wav", "audio3.wav"]
transcriptions = [
    ["n", "yeo", "ng_f"],
    ["g", "a", "m", "s", "a"],
    ["h", "a", "n", "g", "u", "g", "eo"]
]

results = aligner.align_batch(audio_files, transcriptions, "output/batch")
```

## Project Structure

```
kfaligner/
├── kfaligner/           # Main package
│   ├── __init__.py      # Package initialization
│   ├── aligner.py       # Core aligner implementation
│   └── korean_phonemes.py  # Korean phoneme utilities
├── config/              # HTK configuration files
│   ├── config.mfcc      # MFCC feature extraction config
│   ├── config.hvite     # Forced alignment config
│   ├── config.train     # Training config
│   └── proto.hmm        # HMM prototype
├── scripts/             # Utility scripts
│   ├── prepare_data.py  # Data preparation
│   ├── train_models.py  # Model training
│   └── example_usage.py # Usage examples
├── data/                # Sample data
│   └── sample_text.txt  # Sample Korean text
├── requirements.txt     # Python dependencies
├── setup.py            # Package setup
└── README.md           # This file
```

## Korean Phoneme Set

The aligner uses a comprehensive Korean phoneme set:

**Consonants**: g, gg, n, d, dd, r, m, b, bb, s, ss, j, jj, ch, k, t, p, h

**Vowels**: a, ae, ya, yae, eo, e, yeo, ye, o, wa, wae, oe, yo, u, wo, we, wi, yu, eu, ui, i

**Final Consonants**: k_f, n_f, t_f, l_f, m_f, p_f, ng_f

**Special**: sil (silence), sp (short pause)

## HTK Configuration

The system includes pre-configured HTK settings:

- **MFCC Features**: 12 coefficients + energy, with delta and acceleration
- **Frame Rate**: 10ms (100 frames/second)
- **Window Size**: 25ms
- **HMM Topology**: 3-state left-to-right models

## Training Pipeline

1. **Data Preparation**: Convert Korean text to phoneme transcriptions
2. **Feature Extraction**: Extract MFCC features from audio using HCopy
3. **Model Initialization**: Create initial HMM models for each phoneme
4. **Training**: Iteratively train models using HERest
5. **Alignment**: Use HVite for forced alignment with trained models

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

MIT License

## References

- HTK Book: http://htk.eng.cam.ac.uk/docs/docs.shtml
- Korean Phonology: Standard Korean phoneme inventory
- Forced Alignment: HMM-based speech recognition techniques

## Citation

If you use this tool in your research, please cite:

```
@software{kfaligner,
  title={kfaligner: HTK-based Korean Forced Aligner},
  author={exphon},
  url={https://github.com/exphon/kfaligner},
  year={2025}
}
```
