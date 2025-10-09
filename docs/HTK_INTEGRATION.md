# HTK Integration Guide

## Overview

This document explains how kfaligner integrates with the HTK (Hidden Markov Model Toolkit) for Korean forced alignment.

## HTK Tools Used

### 1. HCopy
- **Purpose**: Extract MFCC features from audio files
- **Configuration**: `config/config.mfcc`
- **Input**: WAV audio files
- **Output**: Feature files (.mfc)

### 2. HVite
- **Purpose**: Perform forced alignment
- **Configuration**: `config/config.hvite`
- **Input**: Feature files, HMM models, transcription
- **Output**: Alignment MLF with time boundaries

### 3. HCompV (for training)
- **Purpose**: Initialize HMM variance parameters
- **Used in**: Training pipeline

### 4. HERest (for training)
- **Purpose**: Re-estimate HMM parameters
- **Used in**: Iterative training

## Korean Phoneme Processing

### Hangul Decomposition

Korean characters (Hangul) are decomposed into three components:
- **Initial consonant (초성)**: 19 consonants
- **Medial vowel (중성)**: 21 vowels
- **Final consonant (종성)**: 27 final consonants (optional)

### Phoneme Mapping

Example: 한국어 (Korean language)
- 한: h + a + n_f → ['h', 'a', 'n_f']
- 국: g + u + k_f → ['g', 'u', 'k_f']
- 어: (none) + eo + (none) → ['eo']

Result: ['h', 'a', 'n_f', 'g', 'u', 'k_f', 'eo']

## HMM Model Structure

### Topology
- **Type**: Left-to-right HMM
- **States**: 5 states (including entry and exit)
- **Emitting states**: 3 (states 2, 3, 4)

### Feature Vector
- **Type**: MFCC_0_D_A
- **Dimensions**: 39
  - 13 MFCC coefficients (12 + energy)
  - 13 delta coefficients
  - 13 acceleration coefficients

## Training Pipeline

### Step 1: Data Preparation
```bash
python scripts/prepare_data.py data/text.txt output/data
```

Creates:
- Pronunciation dictionary (dict.txt)
- Phoneme list (phonemes.txt)
- Transcriptions (transcriptions.txt)

### Step 2: Feature Extraction
```bash
# For each audio file
HCopy -C config/config.mfcc audio.wav features.mfc
```

### Step 3: Model Initialization
```bash
python scripts/train_models.py output/data output/models
```

Creates initial HMM models for all phonemes.

### Step 4: Training Iterations
```bash
# Embedded training with HERest
for i in {1..10}; do
    HERest -C config/config.train \
           -I train.mlf \
           -S train.scp \
           -H models/hmmdefs \
           -M models/ \
           models/models.list
done
```

### Step 5: Forced Alignment
```bash
HVite -a -m \
      -I transcription.mlf \
      -H models/hmmdefs \
      -S features.scp \
      -i alignment.mlf \
      -y lab \
      dict.txt \
      models.list
```

## Configuration Parameters

### MFCC Extraction (config.mfcc)
- **TARGETRATE**: 100000.0 (10ms frame rate)
- **WINDOWSIZE**: 250000.0 (25ms window)
- **NUMCHANS**: 26 (filter bank channels)
- **NUMCEPS**: 12 (cepstral coefficients)
- **PREEMCOEF**: 0.97 (pre-emphasis)

### Forced Alignment (config.hvite)
- **PRUNING**: 250.0 (beam pruning threshold)
- **BEAMWIDTH**: 200.0 (beam width)
- **LMSCALE**: 15.0 (language model scale)

## File Formats

### Master Label File (.mlf)
```
#!MLF!#
"utterance1.lab"
sil
h
a
n_f
g
u
k_f
eo
sil
.
```

### Dictionary File (dict.txt)
```
sil sil
sp sp
한국어 h a n_f g u k_f eo
안녕 a n_f n yeo ng_f
```

## Python API Usage

### Basic Alignment
```python
from kfaligner import KoreanForcedAligner
from kfaligner.korean_phonemes import hangul_to_phonemes

aligner = KoreanForcedAligner()
text = "안녕하세요"
phonemes = hangul_to_phonemes(text)
result = aligner.align("audio.wav", phonemes, "output/")
```

### Parsing Results
```python
alignments = aligner.parse_alignment(result)
for file_id, segments in alignments.items():
    for start, end, label in segments:
        start_sec = start / 10000000
        end_sec = end / 10000000
        print(f"{start_sec:.3f}s - {end_sec:.3f}s: {label}")
```

## References

- HTK Book: http://htk.eng.cam.ac.uk/docs/docs.shtml
- Korean Phonology: Standard Korean phoneme system
