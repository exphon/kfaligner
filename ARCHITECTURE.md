# Korean Forced Aligner - Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface                          │
│                   (templates/index.html)                     │
│                                                              │
│  • Upload Audio File (WAV, MP3, FLAC, OGG)                  │
│  • Enter Korean Text Transcription                          │
│  • Display Alignment Results                                │
└──────────────────┬──────────────────────────────────────────┘
                   │ HTTP POST
                   │ /api/align
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                     Flask Web Server                         │
│                        (app.py)                             │
│                                                              │
│  Routes:                                                     │
│  • GET  /          → Serve web interface                   │
│  • POST /api/align → Process alignment request             │
│  • GET  /health    → Health check                          │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              Alignment Processing Logic                      │
│           (perform_alignment function)                       │
│                                                              │
│  1. Receive audio file and Korean text                      │
│  2. Extract audio duration                                  │
│  3. Split text into words                                   │
│  4. Calculate word-level timestamps                         │
│  5. Return alignment results                                │
└─────────────────────────────────────────────────────────────┘
```

## File Structure

```
kfaligner/
├── app.py                  # Main Flask application with routes and alignment logic
├── config.py               # Configuration settings
├── templates/
│   └── index.html         # Web UI with HTML/CSS/JavaScript
├── requirements.txt       # Python dependencies
├── run.sh                 # Quick start script
├── example.py             # API usage examples
├── test_basic.py          # Basic test suite
├── .gitignore            # Git ignore rules
└── README.md             # Documentation
```

## Data Flow

1. **User Upload**
   - User uploads audio file via web interface
   - User enters Korean text transcription
   - Submits form

2. **Request Processing**
   - Form data sent to `/api/align` endpoint
   - Flask validates file type and text
   - Saves uploaded file temporarily

3. **Alignment**
   - Audio duration extracted
   - Text split into Korean words
   - Timestamps calculated for each word
   - Alignment results generated

4. **Response**
   - JSON response with word-level alignments
   - Each word has start/end timestamps
   - Web UI displays results visually

5. **Cleanup**
   - Temporary audio file removed
   - Resources released

## API Specification

### POST /api/align

**Request:**
```
Content-Type: multipart/form-data

audio_file: <binary file data>
text: "안녕하세요 한국어 텍스트"
```

**Response:**
```json
{
  "success": true,
  "alignment": [
    {
      "word": "안녕하세요",
      "start": 0.000,
      "end": 0.567
    },
    {
      "word": "한국어",
      "start": 0.567,
      "end": 1.134
    },
    {
      "word": "텍스트",
      "start": 1.134,
      "end": 1.701
    }
  ],
  "text": "안녕하세요 한국어 텍스트"
}
```

**Error Response:**
```json
{
  "error": "Error message description"
}
```

## Technology Stack

- **Backend:** Python 3.8+, Flask 3.0
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Audio Processing:** Python wave module (built-in)
- **Web Server:** Flask development server (Werkzeug)

## Future Enhancements

For production use, consider integrating:

1. **Advanced Alignment:**
   - Montreal Forced Aligner (MFA)
   - Kaldi speech recognition toolkit
   - Wav2Vec 2.0 models

2. **Korean Language Processing:**
   - KoNLPy for better tokenization
   - Korean phonetic dictionary
   - Syllable-level alignment

3. **Production Features:**
   - User authentication
   - File storage (S3, Azure Blob)
   - Database for results history
   - Async processing with Celery
   - WebSocket for real-time updates
   - Docker containerization
   - Production WSGI server (Gunicorn/uWSGI)

4. **UI Improvements:**
   - Audio waveform visualization
   - Interactive timeline editing
   - Export to various formats (TextGrid, JSON, SRT)
   - Batch processing support
