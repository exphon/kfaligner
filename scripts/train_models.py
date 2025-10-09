#!/usr/bin/env python3
"""
Training script for Korean HMM-based acoustic models using HTK
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def initialize_hmms(phoneme_list, proto_file, output_dir, config_file):
    """
    Initialize HMM models for each phoneme
    
    Args:
        phoneme_list: File containing list of phonemes
        proto_file: Prototype HMM file
        output_dir: Output directory for initialized models
        config_file: HTK config file
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Read phoneme list
    with open(phoneme_list, 'r') as f:
        phonemes = [line.strip() for line in f if line.strip()]
    
    # Create HMM definition file for each phoneme
    hmmdefs_file = os.path.join(output_dir, 'hmmdefs')
    
    with open(hmmdefs_file, 'w') as out:
        # Read prototype
        with open(proto_file, 'r') as proto:
            proto_content = proto.read()
        
        # Write HMM for each phoneme
        for phoneme in phonemes:
            # Replace prototype name with phoneme name
            hmm_content = proto_content.replace('"proto"', f'"{phoneme}"')
            out.write(hmm_content)
            out.write('\n')
    
    print(f"Initialized {len(phonemes)} HMM models in {hmmdefs_file}")
    return hmmdefs_file


def create_model_list(phoneme_list, output_file):
    """
    Create model list file for HTK
    
    Args:
        phoneme_list: File containing list of phonemes
        output_file: Output model list file
    """
    with open(phoneme_list, 'r') as f:
        phonemes = [line.strip() for line in f if line.strip()]
    
    with open(output_file, 'w') as out:
        for phoneme in phonemes:
            out.write(f"{phoneme}\n")
    
    print(f"Created model list: {output_file}")


def train_models(data_dir, model_dir, config_dir, num_iterations=10):
    """
    Train HMM models using HTK
    
    Args:
        data_dir: Directory containing training data
        model_dir: Directory for model files
        config_dir: Directory containing config files
        num_iterations: Number of training iterations
    """
    os.makedirs(model_dir, exist_ok=True)
    
    phoneme_list = os.path.join(data_dir, 'phonemes.txt')
    proto_file = os.path.join(config_dir, 'proto.hmm')
    train_config = os.path.join(config_dir, 'config.train')
    
    # Initialize HMMs
    print("Step 1: Initializing HMM models...")
    hmmdefs_file = initialize_hmms(
        phoneme_list, 
        proto_file, 
        model_dir,
        train_config
    )
    
    # Create model list
    model_list = os.path.join(model_dir, 'models.list')
    create_model_list(phoneme_list, model_list)
    
    print(f"\nTraining setup complete!")
    print(f"  - HMM definitions: {hmmdefs_file}")
    print(f"  - Model list: {model_list}")
    print(f"\nTo complete training, run HERest iterations on your training data.")
    print(f"Example HTK command:")
    print(f"  HERest -C {train_config} -I train.mlf -S train.scp \\")
    print(f"         -H {hmmdefs_file} -M {model_dir} {model_list}")


def main():
    parser = argparse.ArgumentParser(
        description='Train Korean acoustic models for forced alignment'
    )
    parser.add_argument(
        'data_dir',
        help='Directory containing prepared training data'
    )
    parser.add_argument(
        'model_dir',
        help='Output directory for trained models'
    )
    parser.add_argument(
        '--config-dir',
        default=None,
        help='Directory containing HTK config files'
    )
    parser.add_argument(
        '--iterations',
        type=int,
        default=10,
        help='Number of training iterations (default: 10)'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.data_dir):
        print(f"Error: Data directory not found: {args.data_dir}")
        sys.exit(1)
    
    if args.config_dir is None:
        # Use default config directory
        script_dir = Path(__file__).parent
        args.config_dir = script_dir.parent / 'config'
    
    if not os.path.exists(args.config_dir):
        print(f"Error: Config directory not found: {args.config_dir}")
        sys.exit(1)
    
    train_models(args.data_dir, args.model_dir, args.config_dir, args.iterations)


if __name__ == '__main__':
    main()
