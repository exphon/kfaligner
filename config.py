"""
Configuration settings for Korean Forced Aligner
"""
import os

# Flask settings
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', 5000))

# File upload settings
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
ALLOWED_AUDIO_EXTENSIONS = {'wav', 'mp3', 'flac', 'ogg'}

# Alignment settings
DEFAULT_SAMPLE_RATE = 16000
MIN_WORD_DURATION = 0.1  # Minimum word duration in seconds

# Create required directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
