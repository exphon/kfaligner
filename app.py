"""
Korean Forced Aligner Web Application
"""
import os
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_AUDIO_EXTENSIONS'] = {'wav', 'mp3', 'flac', 'ogg'}

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename, allowed_extensions):
    """Check if file has allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/align', methods=['POST'])
def align():
    """
    API endpoint for forced alignment
    Expects:
    - audio_file: audio file (wav, mp3, flac, ogg)
    - text: Korean text transcription
    """
    # Check if audio file is present
    if 'audio_file' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio_file']
    text = request.form.get('text', '')
    
    if audio_file.filename == '':
        return jsonify({'error': 'No audio file selected'}), 400
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    if not allowed_file(audio_file.filename, app.config['ALLOWED_AUDIO_EXTENSIONS']):
        return jsonify({'error': 'Invalid audio file format'}), 400
    
    # Save uploaded file
    filename = secure_filename(audio_file.filename)
    audio_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    audio_file.save(audio_path)
    
    try:
        # Perform forced alignment
        alignment_result = perform_alignment(audio_path, text)
        
        return jsonify({
            'success': True,
            'alignment': alignment_result,
            'text': text
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up uploaded file
        if os.path.exists(audio_path):
            os.remove(audio_path)


def perform_alignment(audio_path, text):
    """
    Perform forced alignment between audio and text
    This is a simplified implementation for demonstration
    In production, this would use Montreal Forced Aligner or similar tool
    """
    import os
    import wave
    
    # Try to get audio duration from WAV file
    duration = 5.0  # default duration
    
    try:
        if audio_path.lower().endswith('.wav'):
            with wave.open(audio_path, 'rb') as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                duration = frames / float(rate)
        else:
            # For non-WAV files, use file size as rough estimate
            # This is a placeholder - in production, use proper audio library
            file_size = os.path.getsize(audio_path)
            # Rough estimate: assume ~128kbps MP3
            duration = file_size / (128 * 1024 / 8)
    except Exception:
        # If we can't determine duration, use default
        pass
    
    # Split Korean text into words/syllables
    words = text.strip().split()
    
    if not words:
        return []
    
    # Simple equal-spacing alignment (placeholder for actual forced alignment)
    # In a real implementation, this would use acoustic models and phonetic dictionaries
    word_duration = duration / len(words)
    
    alignment = []
    for i, word in enumerate(words):
        start_time = i * word_duration
        end_time = (i + 1) * word_duration
        
        alignment.append({
            'word': word,
            'start': round(start_time, 3),
            'end': round(end_time, 3)
        })
    
    return alignment


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
