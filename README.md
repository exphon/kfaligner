# kfaligner
Korean Forced Aligner Web Application

A web-based tool for forced alignment of Korean audio and text. This application helps you align Korean text transcriptions with audio files to get word-level timestamps.

## Features

- 🎤 Upload audio files (WAV, MP3, FLAC, OGG)
- 📝 Input Korean text transcriptions
- ⏱️ Get word-level time alignments
- 🌐 User-friendly web interface
- 🚀 RESTful API for programmatic access

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/exphon/kfaligner.git
cd kfaligner
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

**Note:** If you encounter network issues during installation, you can install packages individually:
```bash
pip install Flask
pip install werkzeug
```

Alternatively, install from a different index or use cached packages.

## Usage

### Quick Start

For the easiest setup, use the quick start script:
```bash
chmod +x run.sh
./run.sh
```

This script will:
1. Create a virtual environment
2. Install dependencies
3. Start the web application

### Docker Deployment (Recommended)

If you have Docker installed, you can run the application in a container:

```bash
# Build and run with docker-compose
docker-compose up

# Or build and run manually
docker build -t kfaligner .
docker run -p 5000:5000 kfaligner
```

Then access the application at http://localhost:5000

### Manual Setup

#### Running the Web Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Upload an audio file and enter the corresponding Korean text, then click "Align" to get results.

### API Usage

You can also use the API programmatically:

```python
import requests

url = 'http://localhost:5000/api/align'
files = {'audio_file': open('audio.wav', 'rb')}
data = {'text': '안녕하세요 한국어 음성 정렬 시스템입니다'}

response = requests.post(url, files=files, data=data)
result = response.json()

if result['success']:
    for item in result['alignment']:
        print(f"{item['word']}: {item['start']}s - {item['end']}s")
```

### API Endpoints

- `GET /` - Main web interface
- `POST /api/align` - Forced alignment endpoint
  - Parameters:
    - `audio_file` (file): Audio file (WAV, MP3, FLAC, OGG)
    - `text` (string): Korean text transcription
  - Returns: JSON with alignment results
- `GET /health` - Health check endpoint

## How It Works

The forced aligner:
1. Accepts an audio file and Korean text transcription
2. Processes the audio to extract acoustic features
3. Aligns the text with the audio timeline
4. Returns word-level timestamps showing when each word is spoken

**Note:** The current implementation uses a simplified alignment algorithm for demonstration. For production use, consider integrating with more sophisticated tools like:
- Montreal Forced Aligner (MFA)
- Kaldi
- Wav2Vec 2.0

## Project Structure

```
kfaligner/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Web interface
├── requirements.txt      # Python dependencies
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Development

To contribute to this project:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the MIT License.

## Documentation

- 📖 **[Getting Started Guide](GETTING_STARTED.md)** - Step-by-step tutorial for your first alignment
- 🏗️ **[Architecture Documentation](ARCHITECTURE.md)** - Technical details and system design
- 🤝 **[Contributing Guidelines](CONTRIBUTING.md)** - How to contribute to the project
- 📋 **[Project Summary](PROJECT_SUMMARY.md)** - Complete overview of what's implemented

## Acknowledgments

- Built with Flask web framework
- Audio processing powered by librosa
- Inspired by Montreal Forced Aligner
