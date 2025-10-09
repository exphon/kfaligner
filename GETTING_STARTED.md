# Getting Started with Korean Forced Aligner

This guide will walk you through your first alignment in just a few minutes!

## Prerequisites

- Python 3.8 or higher
- A Korean audio file (WAV, MP3, FLAC, or OGG)
- The corresponding Korean text transcription

Don't have audio yet? No problem! We'll generate a test file.

## Quick Start (5 minutes)

### Step 1: Install the Application

Choose one of these methods:

#### Option A: Using Docker (Easiest)
```bash
docker-compose up
```
Then skip to Step 3!

#### Option B: Using the Quick Start Script
```bash
chmod +x run.sh
./run.sh
```
Then skip to Step 3!

#### Option C: Manual Installation
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install Flask werkzeug

# Start the server
python app.py
```

### Step 2: Start the Server

If you didn't use Option A or B above, start the server:
```bash
python app.py
```

You should see output like:
```
 * Running on http://127.0.0.1:5000
```

### Step 3: Open the Web Interface

Open your web browser and navigate to:
```
http://localhost:5000
```

You should see the Korean Forced Aligner interface!

### Step 4: Prepare Test Audio (Optional)

If you don't have audio, generate a test file:
```bash
python generate_test_audio.py my_test.wav 5.0
```

This creates a 5-second test audio file.

### Step 5: Perform Your First Alignment

1. **Upload Audio**: Click "Choose File" and select your audio file
   - Supported formats: WAV, MP3, FLAC, OGG
   - Maximum size: 50MB

2. **Enter Korean Text**: Type or paste your Korean text transcription
   ```
   Example: 안녕하세요 한국어 음성 정렬 시스템입니다
   ```

3. **Click Align**: Press the "Align" button

4. **View Results**: The results will show:
   - Each Korean word
   - Start time (in seconds)
   - End time (in seconds)
   - Duration

Example result:
```
안녕하세요    0.000s - 0.625s (0.625s)
한국어        0.625s - 1.250s (0.625s)
음성          1.250s - 1.875s (0.625s)
정렬          1.875s - 2.500s (0.625s)
시스템입니다  2.500s - 3.125s (0.625s)
```

## Using the API Programmatically

You can also use the API from your own code:

### Python Example

```python
import requests

# Upload audio and text
url = 'http://localhost:5000/api/align'
files = {'audio_file': open('my_audio.wav', 'rb')}
data = {'text': '안녕하세요 테스트입니다'}

response = requests.post(url, files=files, data=data)
result = response.json()

# Print results
if result['success']:
    for item in result['alignment']:
        print(f"{item['word']}: {item['start']:.3f}s - {item['end']:.3f}s")
```

### cURL Example

```bash
curl -X POST http://localhost:5000/api/align \
  -F "audio_file=@my_audio.wav" \
  -F "text=안녕하세요 테스트입니다"
```

### JavaScript Example

```javascript
const formData = new FormData();
formData.append('audio_file', audioFile);
formData.append('text', '안녕하세요 테스트입니다');

fetch('http://localhost:5000/api/align', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        data.alignment.forEach(item => {
            console.log(`${item.word}: ${item.start}s - ${item.end}s`);
        });
    }
});
```

## Common Issues

### "No module named 'flask'"
Install Flask: `pip install Flask`

### "Connection refused" or "Cannot connect"
Make sure the server is running: `python app.py`

### "Invalid audio file format"
Ensure your audio is in WAV, MP3, FLAC, or OGG format

### "No audio file provided"
Make sure you selected a file before clicking Align

## Next Steps

Now that you've done your first alignment:

1. **Try with real audio**: Use actual Korean speech audio
2. **Experiment with text**: Try different Korean sentences
3. **Explore the API**: Integrate with your own applications
4. **Read the docs**: Check out ARCHITECTURE.md for details

## Advanced Usage

### Processing Multiple Files

Create a batch processing script:

```python
import os
import requests

audio_dir = 'audio_files/'
texts = {
    'file1.wav': '첫 번째 텍스트',
    'file2.wav': '두 번째 텍스트',
}

for filename, text in texts.items():
    audio_path = os.path.join(audio_dir, filename)
    
    files = {'audio_file': open(audio_path, 'rb')}
    data = {'text': text}
    
    response = requests.post('http://localhost:5000/api/align', 
                           files=files, data=data)
    result = response.json()
    
    print(f"\nResults for {filename}:")
    for item in result['alignment']:
        print(f"  {item['word']}: {item['start']:.3f}s - {item['end']:.3f}s")
```

### Exporting Results

Save results to a file:

```python
import json

# ... perform alignment ...

# Save as JSON
with open('alignment_results.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

# Save as CSV
import csv
with open('alignment_results.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Word', 'Start', 'End', 'Duration'])
    for item in result['alignment']:
        duration = item['end'] - item['start']
        writer.writerow([item['word'], item['start'], item['end'], duration])
```

## Getting Help

- Check the README.md for full documentation
- Read ARCHITECTURE.md to understand how it works
- See CONTRIBUTING.md if you want to contribute
- Open an issue on GitHub for bugs or questions

Happy aligning! 🎤🇰🇷
