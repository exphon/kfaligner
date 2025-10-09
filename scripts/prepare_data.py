#!/usr/bin/env python3
"""
Script to prepare training data for Korean forced aligner
"""

import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kfaligner.korean_phonemes import (
    create_pronunciation_dict, 
    create_phoneme_list,
    hangul_to_phonemes
)


def prepare_data(text_file, output_dir):
    """
    Prepare training data from text file
    
    Args:
        text_file: Path to file containing Korean text (one utterance per line)
        output_dir: Directory to save prepared data
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Read text file
    with open(text_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    # Extract unique words
    words = set()
    for line in lines:
        words.update(line.split())
    
    # Create pronunciation dictionary
    dict_file = os.path.join(output_dir, 'dict.txt')
    create_pronunciation_dict(list(words), dict_file)
    print(f"Created pronunciation dictionary: {dict_file}")
    
    # Create phoneme list
    phoneme_file = os.path.join(output_dir, 'phonemes.txt')
    create_phoneme_list(phoneme_file)
    print(f"Created phoneme list: {phoneme_file}")
    
    # Create transcriptions
    trans_file = os.path.join(output_dir, 'transcriptions.txt')
    with open(trans_file, 'w', encoding='utf-8') as f:
        for i, line in enumerate(lines):
            phonemes = hangul_to_phonemes(line)
            phoneme_str = ' '.join(phonemes)
            f.write(f"utt_{i:04d} {phoneme_str}\n")
    
    print(f"Created transcriptions: {trans_file}")
    print(f"\nProcessed {len(lines)} utterances with {len(words)} unique words")


def main():
    parser = argparse.ArgumentParser(
        description='Prepare Korean text data for forced alignment'
    )
    parser.add_argument(
        'text_file',
        help='Input text file (one utterance per line)'
    )
    parser.add_argument(
        'output_dir',
        help='Output directory for prepared data'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.text_file):
        print(f"Error: Text file not found: {args.text_file}")
        sys.exit(1)
    
    prepare_data(args.text_file, args.output_dir)


if __name__ == '__main__':
    main()
