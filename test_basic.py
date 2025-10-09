"""
Basic tests for Korean Forced Aligner
"""
import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test that all imports work"""
    try:
        import app
        import config
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_alignment_function():
    """Test the alignment function"""
    try:
        from app import perform_alignment
        
        # Test with simple text
        # Note: We need a real audio file for this to work fully
        # This is a basic structure test
        text = "안녕하세요 테스트입니다"
        
        # Without an actual audio file, we can't fully test
        # but we can verify the function exists and is callable
        assert callable(perform_alignment)
        print("✓ Alignment function is callable")
        return True
    except Exception as e:
        print(f"✗ Alignment function test failed: {e}")
        return False


def test_flask_app_creation():
    """Test that Flask app can be created"""
    try:
        from app import app
        
        assert app is not None
        assert app.config['UPLOAD_FOLDER'] == 'uploads'
        print("✓ Flask app created successfully")
        print(f"  - Upload folder: {app.config['UPLOAD_FOLDER']}")
        print(f"  - Max file size: {app.config['MAX_CONTENT_LENGTH'] / (1024*1024)}MB")
        return True
    except Exception as e:
        print(f"✗ Flask app creation failed: {e}")
        return False


def test_routes():
    """Test that routes are registered"""
    try:
        from app import app
        
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        
        expected_routes = ['/', '/api/align', '/health']
        
        for route in expected_routes:
            if route in rules:
                print(f"✓ Route '{route}' registered")
            else:
                print(f"✗ Route '{route}' not found")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Route test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("Korean Forced Aligner - Basic Tests")
    print("=" * 50)
    print()
    
    tests = [
        ("Import Test", test_imports),
        ("Alignment Function Test", test_alignment_function),
        ("Flask App Creation Test", test_flask_app_creation),
        ("Routes Test", test_routes),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        print("-" * 50)
        result = test_func()
        results.append(result)
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
