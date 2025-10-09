"""
Korean phoneme utilities for forced alignment
"""

from typing import List, Dict
import re


# Korean phoneme set based on Korean phonology
KOREAN_PHONEMES = {
    # Consonants (초성 - Initial)
    'ㄱ': 'g', 'ㄲ': 'gg', 'ㄴ': 'n', 'ㄷ': 'd', 'ㄸ': 'dd',
    'ㄹ': 'r', 'ㅁ': 'm', 'ㅂ': 'b', 'ㅃ': 'bb', 'ㅅ': 's',
    'ㅆ': 'ss', 'ㅇ': '', 'ㅈ': 'j', 'ㅉ': 'jj', 'ㅊ': 'ch',
    'ㅋ': 'k', 'ㅌ': 't', 'ㅍ': 'p', 'ㅎ': 'h',
    
    # Vowels (중성 - Medial)
    'ㅏ': 'a', 'ㅐ': 'ae', 'ㅑ': 'ya', 'ㅒ': 'yae', 'ㅓ': 'eo',
    'ㅔ': 'e', 'ㅕ': 'yeo', 'ㅖ': 'ye', 'ㅗ': 'o', 'ㅘ': 'wa',
    'ㅙ': 'wae', 'ㅚ': 'oe', 'ㅛ': 'yo', 'ㅜ': 'u', 'ㅝ': 'wo',
    'ㅞ': 'we', 'ㅟ': 'wi', 'ㅠ': 'yu', 'ㅡ': 'eu', 'ㅢ': 'ui',
    'ㅣ': 'i',
    
    # Final consonants (종성 - Final)
    'ㄱ_f': 'k_f', 'ㄲ_f': 'k_f', 'ㄳ_f': 'k_f',
    'ㄴ_f': 'n_f', 'ㄵ_f': 'n_f', 'ㄶ_f': 'n_f',
    'ㄷ_f': 't_f', 'ㄹ_f': 'l_f', 'ㄺ_f': 'l_f', 'ㄻ_f': 'm_f',
    'ㄼ_f': 'l_f', 'ㄽ_f': 'l_f', 'ㄾ_f': 'l_f', 'ㄿ_f': 'p_f',
    'ㅀ_f': 'l_f', 'ㅁ_f': 'm_f', 'ㅂ_f': 'p_f', 'ㅄ_f': 'p_f',
    'ㅅ_f': 't_f', 'ㅆ_f': 't_f', 'ㅇ_f': 'ng_f', 'ㅈ_f': 't_f',
    'ㅊ_f': 't_f', 'ㅋ_f': 'k_f', 'ㅌ_f': 't_f', 'ㅍ_f': 'p_f',
    'ㅎ_f': 't_f'
}


# HTK phoneme set for Korean
HTK_PHONEME_SET = [
    # Consonants
    'g', 'gg', 'n', 'd', 'dd', 'r', 'm', 'b', 'bb', 's', 'ss',
    'j', 'jj', 'ch', 'k', 't', 'p', 'h',
    
    # Vowels
    'a', 'ae', 'ya', 'yae', 'eo', 'e', 'yeo', 'ye', 'o', 'wa',
    'wae', 'oe', 'yo', 'u', 'wo', 'we', 'wi', 'yu', 'eu', 'ui', 'i',
    
    # Final consonants
    'k_f', 'n_f', 't_f', 'l_f', 'm_f', 'p_f', 'ng_f',
    
    # Special
    'sil', 'sp'  # silence and short pause
]


def decompose_hangul(char: str) -> tuple:
    """
    Decompose a Hangul character into initial, medial, and final components
    
    Args:
        char: Single Hangul character
        
    Returns:
        Tuple of (initial, medial, final) indices
    """
    if not ('가' <= char <= '힣'):
        return None
    
    code = ord(char) - ord('가')
    initial = code // 588
    medial = (code % 588) // 28
    final = code % 28
    
    return (initial, medial, final)


# Jamo tables
INITIALS = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
MEDIALS = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
FINALS = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']


def hangul_to_phonemes(text: str) -> List[str]:
    """
    Convert Korean text to phoneme sequence
    
    Args:
        text: Korean text string
        
    Returns:
        List of phonemes in HTK format
    """
    phonemes = []
    
    for char in text:
        if '가' <= char <= '힣':
            decomposed = decompose_hangul(char)
            if decomposed:
                initial_idx, medial_idx, final_idx = decomposed
                
                # Add initial consonant
                initial = INITIALS[initial_idx]
                if initial != 'ㅇ':  # ㅇ in initial position is silent
                    initial_phoneme = KOREAN_PHONEMES.get(initial, '')
                    if initial_phoneme:
                        phonemes.append(initial_phoneme)
                
                # Add vowel
                medial = MEDIALS[medial_idx]
                medial_phoneme = KOREAN_PHONEMES.get(medial, '')
                if medial_phoneme:
                    phonemes.append(medial_phoneme)
                
                # Add final consonant
                if final_idx > 0:
                    final = FINALS[final_idx]
                    final_key = final + '_f'
                    final_phoneme = KOREAN_PHONEMES.get(final_key, '')
                    if final_phoneme:
                        phonemes.append(final_phoneme)
        elif char == ' ':
            # Add short pause for spaces
            if phonemes and phonemes[-1] != 'sp':
                phonemes.append('sp')
    
    return phonemes


def create_pronunciation_dict(words: List[str], output_file: str):
    """
    Create HTK pronunciation dictionary from Korean words
    
    Args:
        words: List of Korean words
        output_file: Output dictionary file path
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        # Add silence models
        f.write("sil sil\n")
        f.write("sp sp\n")
        
        # Add words with their phoneme pronunciations
        for word in sorted(set(words)):
            phonemes = hangul_to_phonemes(word)
            if phonemes:
                phoneme_str = ' '.join(phonemes)
                f.write(f"{word} {phoneme_str}\n")


def create_phoneme_list(output_file: str):
    """
    Create list of all phonemes for HTK
    
    Args:
        output_file: Output file path
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for phoneme in sorted(HTK_PHONEME_SET):
            f.write(f"{phoneme}\n")
