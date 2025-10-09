"""
Integration test for Korean Forced Aligner
Tests the complete flow: generate audio, upload, and get alignment results
"""
import os
import sys
import json

# Test if we can generate audio
try:
    import generate_test_audio
    has_audio_gen = True
except ImportError:
    has_audio_gen = False
    print("Warning: Cannot import audio generation module")


def test_audio_generation():
    """Test generating a sample audio file"""
    if not has_audio_gen:
        print("✗ Audio generation module not available")
        return False
    
    try:
        test_file = '/tmp/test_korean_audio.wav'
        generate_test_audio.generate_test_audio(test_file, duration=2.0)
        
        if os.path.exists(test_file):
            file_size = os.path.getsize(test_file)
            print(f"✓ Test audio generated: {file_size} bytes")
            return True
        else:
            print("✗ Audio file was not created")
            return False
    except Exception as e:
        print(f"✗ Audio generation failed: {e}")
        return False


def test_alignment_with_test_audio():
    """Test the alignment function with generated audio"""
    try:
        from app import perform_alignment
        
        # Generate test audio
        test_file = '/tmp/test_korean_audio.wav'
        if has_audio_gen:
            generate_test_audio.generate_test_audio(test_file, duration=2.0)
        
        if not os.path.exists(test_file):
            print("✗ Test audio file not available")
            return False
        
        # Test with Korean text
        korean_text = "안녕하세요 테스트입니다"
        
        result = perform_alignment(test_file, korean_text)
        
        if not result:
            print("✗ Alignment returned no results")
            return False
        
        print(f"✓ Alignment successful with {len(result)} words")
        
        # Validate result structure
        for i, item in enumerate(result):
            if 'word' not in item or 'start' not in item or 'end' not in item:
                print(f"✗ Invalid result structure at index {i}")
                return False
            
            if item['start'] >= item['end']:
                print(f"✗ Invalid timing: start >= end for '{item['word']}'")
                return False
            
            print(f"  Word {i+1}: '{item['word']}' [{item['start']:.3f}s - {item['end']:.3f}s]")
        
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
        
        return True
        
    except Exception as e:
        print(f"✗ Alignment test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_endpoint():
    """Test the API endpoint with test audio"""
    try:
        from app import app
        
        # Create test client
        client = app.test_client()
        
        # Test health endpoint
        response = client.get('/health')
        if response.status_code == 200:
            print("✓ Health endpoint working")
        else:
            print(f"✗ Health endpoint returned {response.status_code}")
            return False
        
        # Test main page
        response = client.get('/')
        if response.status_code == 200:
            print("✓ Main page loads successfully")
        else:
            print(f"✗ Main page returned {response.status_code}")
            return False
        
        # Test alignment endpoint with actual file
        if has_audio_gen:
            test_file = '/tmp/test_api_audio.wav'
            generate_test_audio.generate_test_audio(test_file, duration=2.0)
            
            if os.path.exists(test_file):
                with open(test_file, 'rb') as f:
                    data = {
                        'text': '안녕하세요 테스트',
                        'audio_file': (f, 'test.wav')
                    }
                    response = client.post('/api/align', 
                                          data=data,
                                          content_type='multipart/form-data')
                
                if response.status_code == 200:
                    result = json.loads(response.data)
                    if result.get('success'):
                        print(f"✓ API alignment successful")
                        print(f"  Aligned {len(result['alignment'])} words")
                        return True
                    else:
                        print(f"✗ API returned error: {result.get('error')}")
                        return False
                else:
                    print(f"✗ API endpoint returned {response.status_code}")
                    return False
                
                # Cleanup
                if os.path.exists(test_file):
                    os.remove(test_file)
        else:
            print("⊘ Skipping API file upload test (no audio generation)")
            return True
        
    except Exception as e:
        print(f"✗ API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run integration tests"""
    print("Korean Forced Aligner - Integration Tests")
    print("=" * 60)
    print()
    
    tests = [
        ("Audio Generation Test", test_audio_generation),
        ("Alignment with Test Audio", test_alignment_with_test_audio),
        ("API Endpoint Test", test_api_endpoint),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        print("-" * 60)
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"✗ Test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 60)
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("✓ All integration tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
