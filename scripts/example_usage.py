#!/usr/bin/env python3
"""
Example script demonstrating Korean forced alignment
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kfaligner import KoreanForcedAligner
from kfaligner.korean_phonemes import hangul_to_phonemes


def example_alignment():
    """
    Example of using the Korean Forced Aligner
    """
    # Initialize aligner
    aligner = KoreanForcedAligner()
    
    # Example Korean text
    korean_text = "안녕하세요"
    
    # Convert to phonemes
    phonemes = hangul_to_phonemes(korean_text)
    print(f"Korean text: {korean_text}")
    print(f"Phonemes: {' '.join(phonemes)}")
    
    # Example alignment (requires audio file and trained models)
    # audio_file = "path/to/audio.wav"
    # output_dir = "output"
    # result = aligner.align(audio_file, phonemes, output_dir)
    # 
    # if result:
    #     alignments = aligner.parse_alignment(result)
    #     for file_id, segments in alignments.items():
    #         print(f"\nAlignment for {file_id}:")
    #         for start, end, label in segments:
    #             print(f"  {start/10000000:.3f}s - {end/10000000:.3f}s: {label}")
    
    print("\nNote: To perform actual alignment, you need:")
    print("  1. Audio files in WAV format")
    print("  2. Trained HMM models (or use the training pipeline)")
    print("  3. HTK toolkit installed and in PATH")


def example_batch_processing():
    """
    Example of batch processing multiple files
    """
    aligner = KoreanForcedAligner()
    
    # Example texts
    texts = [
        "안녕하세요",
        "감사합니다",
        "좋은 하루 되세요"
    ]
    
    # Convert all to phonemes
    phoneme_sequences = [hangul_to_phonemes(text) for text in texts]
    
    print("Batch conversion examples:")
    for text, phonemes in zip(texts, phoneme_sequences):
        print(f"{text}: {' '.join(phonemes)}")


if __name__ == '__main__':
    print("="*60)
    print("Korean Forced Aligner - Example Usage")
    print("="*60)
    print()
    
    example_alignment()
    print()
    print("-"*60)
    print()
    example_batch_processing()
