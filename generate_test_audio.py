"""
Generate sample WAV file for testing the Korean Forced Aligner
This creates a simple sine wave audio file that can be used for testing
without requiring actual Korean speech audio.
"""
import wave
import math
import struct


def generate_sine_wave(frequency, duration, sample_rate=16000, amplitude=0.5):
    """
    Generate a sine wave
    
    Args:
        frequency: Frequency in Hz
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
        amplitude: Amplitude (0.0 to 1.0)
    
    Returns:
        List of audio samples
    """
    samples = []
    num_samples = int(duration * sample_rate)
    
    for i in range(num_samples):
        t = i / sample_rate
        sample = amplitude * math.sin(2 * math.pi * frequency * t)
        # Convert to 16-bit integer
        sample_int = int(sample * 32767)
        samples.append(sample_int)
    
    return samples


def save_wav_file(filename, samples, sample_rate=16000):
    """
    Save samples to a WAV file
    
    Args:
        filename: Output filename
        samples: List of audio samples
        sample_rate: Sample rate in Hz
    """
    with wave.open(filename, 'wb') as wav_file:
        # Set parameters: 1 channel, 2 bytes per sample, sample_rate
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        # Write samples
        for sample in samples:
            wav_file.writeframes(struct.pack('h', sample))


def generate_test_audio(filename='test_audio.wav', duration=3.0):
    """
    Generate a test audio file
    
    Args:
        filename: Output filename
        duration: Duration in seconds
    """
    print(f"Generating test audio file: {filename}")
    print(f"Duration: {duration} seconds")
    
    # Generate a pleasant multi-tone sound
    sample_rate = 16000
    all_samples = []
    
    # Create multiple tones at different frequencies
    frequencies = [440, 554, 659]  # A, C#, E (A major chord)
    
    for freq in frequencies:
        samples = generate_sine_wave(freq, duration, sample_rate, amplitude=0.2)
        
        # Add to combined samples
        if not all_samples:
            all_samples = samples
        else:
            # Mix the tones together
            all_samples = [a + b for a, b in zip(all_samples, samples)]
    
    # Normalize to prevent clipping
    max_val = max(abs(s) for s in all_samples)
    if max_val > 32767:
        all_samples = [int(s * 32767 / max_val) for s in all_samples]
    
    save_wav_file(filename, all_samples, sample_rate)
    print(f"✓ Test audio file created successfully")
    print(f"  Sample rate: {sample_rate} Hz")
    print(f"  Duration: {duration} seconds")
    print(f"  File size: ~{len(all_samples) * 2 / 1024:.1f} KB")
    print()
    print("You can use this file to test the aligner with Korean text:")
    print("  Example text: 안녕하세요 테스트입니다")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = 'test_audio.wav'
    
    if len(sys.argv) > 2:
        duration = float(sys.argv[2])
    else:
        duration = 3.0
    
    generate_test_audio(filename, duration)
