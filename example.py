"""
Example script showing how to use the Korean Forced Aligner API
"""
import requests
import json


def align_audio_text(audio_path, text, api_url='http://localhost:5000/api/align'):
    """
    Send audio and text to the forced aligner API
    
    Args:
        audio_path: Path to the audio file
        text: Korean text transcription
        api_url: URL of the API endpoint
    
    Returns:
        Alignment results as a dictionary
    """
    try:
        with open(audio_path, 'rb') as audio_file:
            files = {'audio_file': audio_file}
            data = {'text': text}
            
            response = requests.post(api_url, files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result
                else:
                    print(f"Error: {result.get('error', 'Unknown error')}")
                    return None
            else:
                print(f"HTTP Error {response.status_code}: {response.text}")
                return None
                
    except FileNotFoundError:
        print(f"Error: Audio file not found: {audio_path}")
        return None
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure the server is running.")
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


def print_alignment(result):
    """Pretty print alignment results"""
    if not result:
        return
    
    print("\n" + "="*60)
    print("ALIGNMENT RESULTS")
    print("="*60)
    print(f"\nOriginal Text: {result.get('text', '')}\n")
    
    alignment = result.get('alignment', [])
    
    if not alignment:
        print("No alignment data available.")
        return
    
    print(f"{'Word':<20} {'Start (s)':<12} {'End (s)':<12} {'Duration (s)'}")
    print("-"*60)
    
    for item in alignment:
        word = item.get('word', '')
        start = item.get('start', 0)
        end = item.get('end', 0)
        duration = end - start
        
        print(f"{word:<20} {start:<12.3f} {end:<12.3f} {duration:.3f}")
    
    print("="*60 + "\n")


def main():
    """Example usage"""
    # Example 1: Basic usage
    print("Example: Using the Korean Forced Aligner API\n")
    
    # Note: You need to provide your own audio file
    audio_path = 'example_audio.wav'
    korean_text = '안녕하세요 한국어 음성 정렬 시스템입니다'
    
    print(f"Audio file: {audio_path}")
    print(f"Text: {korean_text}\n")
    print("Sending request to API...")
    
    result = align_audio_text(audio_path, korean_text)
    
    if result:
        print_alignment(result)
    else:
        print("\nAlignment failed. Please check:")
        print("1. The Flask server is running (python app.py)")
        print("2. The audio file exists and is in a supported format")
        print("3. The text is provided correctly")


if __name__ == '__main__':
    main()
