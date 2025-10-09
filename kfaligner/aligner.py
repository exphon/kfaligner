"""
Main Korean Forced Aligner implementation using HTK
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KoreanForcedAligner:
    """
    HTK-based forced aligner for Korean speech
    
    This class implements a forced alignment system that aligns Korean phonetic
    transcriptions with audio files using the Hidden Markov Model Toolkit (HTK).
    """
    
    def __init__(self, htk_path: Optional[str] = None, 
                 model_dir: Optional[str] = None,
                 config_dir: Optional[str] = None):
        """
        Initialize the Korean Forced Aligner
        
        Args:
            htk_path: Path to HTK binaries (default: assumes HTK in PATH)
            model_dir: Directory containing acoustic models
            config_dir: Directory containing HTK configuration files
        """
        self.htk_path = htk_path or ""
        self.model_dir = model_dir or os.path.join(os.path.dirname(__file__), "..", "models")
        self.config_dir = config_dir or os.path.join(os.path.dirname(__file__), "..", "config")
        
        # HTK tool paths
        self.hvite = os.path.join(self.htk_path, "HVite") if self.htk_path else "HVite"
        self.hcopy = os.path.join(self.htk_path, "HCopy") if self.htk_path else "HCopy"
        self.hcompv = os.path.join(self.htk_path, "HCompV") if self.htk_path else "HCompV"
        self.herest = os.path.join(self.htk_path, "HERest") if self.htk_path else "HERest"
        
        logger.info(f"Initialized Korean Forced Aligner")
        logger.info(f"Model directory: {self.model_dir}")
        logger.info(f"Config directory: {self.config_dir}")
    
    def extract_features(self, audio_file: str, output_file: str, 
                        config_file: Optional[str] = None) -> bool:
        """
        Extract MFCC features from audio file using HCopy
        
        Args:
            audio_file: Input audio file (WAV format)
            output_file: Output feature file (.mfc)
            config_file: HTK config file for feature extraction
            
        Returns:
            True if successful, False otherwise
        """
        if config_file is None:
            config_file = os.path.join(self.config_dir, "config.mfcc")
        
        cmd = [self.hcopy, "-C", config_file, audio_file, output_file]
        
        try:
            logger.info(f"Extracting features from {audio_file}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Features saved to {output_file}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Feature extraction failed: {e.stderr}")
            return False
    
    def create_mlf(self, transcriptions: Dict[str, List[str]], output_file: str):
        """
        Create Master Label File (MLF) for HTK
        
        Args:
            transcriptions: Dictionary mapping audio file IDs to phoneme sequences
            output_file: Output MLF file path
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("#!MLF!#\n")
            for file_id, phonemes in transcriptions.items():
                f.write(f'"{file_id}.lab"\n')
                for phoneme in phonemes:
                    f.write(f"{phoneme}\n")
                f.write(".\n")
        
        logger.info(f"Created MLF file: {output_file}")
    
    def align(self, audio_file: str, transcription: List[str], 
              output_dir: str, dictionary: Optional[str] = None,
              model_list: Optional[str] = None) -> Optional[str]:
        """
        Perform forced alignment on audio with transcription
        
        Args:
            audio_file: Input audio file
            transcription: List of phonemes/words to align
            output_dir: Directory for output alignment files
            dictionary: Pronunciation dictionary file
            model_list: HMM model list file
            
        Returns:
            Path to alignment output file, or None if failed
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract features
        feature_file = os.path.join(output_dir, "features.mfc")
        if not self.extract_features(audio_file, feature_file):
            return None
        
        # Create transcription MLF
        file_id = Path(audio_file).stem
        mlf_file = os.path.join(output_dir, "transcription.mlf")
        self.create_mlf({file_id: transcription}, mlf_file)
        
        # Set default paths
        if dictionary is None:
            dictionary = os.path.join(self.config_dir, "dict.txt")
        if model_list is None:
            model_list = os.path.join(self.model_dir, "models.list")
        
        # Run HVite for forced alignment
        output_mlf = os.path.join(output_dir, "alignment.mlf")
        config_file = os.path.join(self.config_dir, "config.hvite")
        
        cmd = [
            self.hvite,
            "-a",  # Perform alignment
            "-m",  # Output model alignment
            "-I", mlf_file,  # Input label MLF
            "-H", os.path.join(self.model_dir, "hmmdefs"),  # HMM definitions
            "-S", feature_file,  # Script file (or single file)
            "-i", output_mlf,  # Output MLF
            "-y", "lab",  # Label format
            dictionary,
            model_list
        ]
        
        try:
            logger.info(f"Running forced alignment on {audio_file}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Alignment completed: {output_mlf}")
            return output_mlf
        except subprocess.CalledProcessError as e:
            logger.error(f"Alignment failed: {e.stderr}")
            return None
    
    def parse_alignment(self, mlf_file: str) -> Dict[str, List[Tuple[int, int, str]]]:
        """
        Parse alignment MLF file into structured format
        
        Args:
            mlf_file: Path to alignment MLF file
            
        Returns:
            Dictionary mapping file IDs to list of (start_time, end_time, label) tuples
        """
        alignments = {}
        current_file = None
        
        with open(mlf_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                if line.startswith('"') and line.endswith('"'):
                    # New file entry
                    current_file = line.strip('"').replace('.lab', '')
                    alignments[current_file] = []
                elif line == '.' or line == '#!MLF!#':
                    # End of file entry or header
                    continue
                elif current_file and line:
                    # Alignment line: start_time end_time label [score]
                    parts = line.split()
                    if len(parts) >= 3:
                        start_time = int(parts[0])
                        end_time = int(parts[1])
                        label = parts[2]
                        alignments[current_file].append((start_time, end_time, label))
        
        return alignments
    
    def align_batch(self, audio_files: List[str], transcriptions: List[List[str]],
                   output_dir: str) -> List[Optional[str]]:
        """
        Perform batch forced alignment
        
        Args:
            audio_files: List of input audio files
            transcriptions: List of phoneme sequences for each audio file
            output_dir: Directory for output files
            
        Returns:
            List of alignment file paths (None for failed alignments)
        """
        results = []
        for audio_file, transcription in zip(audio_files, transcriptions):
            file_output_dir = os.path.join(output_dir, Path(audio_file).stem)
            result = self.align(audio_file, transcription, file_output_dir)
            results.append(result)
        
        return results
