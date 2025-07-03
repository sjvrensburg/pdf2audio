#!/usr/bin/env python3
"""
Test script for PDF2Audio API
"""

import requests
import time
import sys
import os
from pathlib import Path

API_BASE = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health check passed: {data['status']}")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False

def test_voices():
    """Test voices endpoint"""
    print("Testing voices endpoint...")
    try:
        response = requests.get(f"{API_BASE}/voices", timeout=10)
        if response.status_code == 200:
            data = response.json()
            voices = data.get('voices', {})
            print(f"✓ Voices loaded: {len(voices)} languages")
            for lang, voice_list in voices.items():
                print(f"  {lang}: {len(voice_list)} voices")
            return True
        else:
            print(f"✗ Voices request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Voices request error: {e}")
        return False

def create_test_pdf():
    """Create a simple test PDF with text content"""
    test_content = """
    # Test Document for PDF2Audio

    This is a test document to verify the PDF2Audio conversion system.

    ## Mathematical Content

    Here are some mathematical expressions:
    - Simple equation: E = mc²
    - Fraction: 1/2 + 3/4 = 5/4
    - Square root: √16 = 4
    - Integral: ∫ x dx = x²/2 + C

    ## Regular Text

    This document contains both regular text and mathematical notation
    to test the complete processing pipeline including:

    1. PDF text extraction with GROBID
    2. Mathematical expression processing with MathJax SRE
    3. Text-to-speech synthesis with Piper TTS

    The system should handle this content and produce natural-sounding audio
    with proper pronunciation of mathematical expressions.
    """
    
    # For this test, we'll create a simple text file and rename it
    # In a real scenario, you'd use a proper PDF
    test_file = Path("test_document.txt")
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    return test_file

def test_upload_and_process():
    """Test file upload and processing"""
    print("Testing file upload and processing...")
    
    # Create test file (simulating PDF)
    test_file = create_test_pdf()
    
    try:
        # Upload file
        with open(test_file, 'rb') as f:
            files = {'file': f}
            data = {
                'language': 'en',
                'voice': 'en_US-lessac-medium',
                'speed': '1.0'
            }
            
            response = requests.post(f"{API_BASE}/upload", files=files, data=data, timeout=30)
        
        if response.status_code == 202:
            upload_data = response.json()
            task_id = upload_data['task_id']
            print(f"✓ Upload successful: {task_id}")
            
            # Poll for status
            print("Monitoring processing status...")
            max_attempts = 60  # 2 minutes max
            attempt = 0
            
            while attempt < max_attempts:
                try:
                    status_response = requests.get(f"{API_BASE}/status/{task_id}", timeout=10)
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        state = status_data.get('state', 'UNKNOWN')
                        stage = status_data.get('stage', 'unknown')
                        progress = status_data.get('progress', 0)
                        message = status_data.get('message', '')
                        
                        print(f"  Status: {state} | Stage: {stage} | Progress: {progress}% | {message}")
                        
                        if state == 'SUCCESS':
                            print("✓ Processing completed successfully!")
                            
                            # Test audio endpoint
                            audio_response = requests.head(f"{API_BASE}/audio/{task_id}")
                            if audio_response.status_code == 200:
                                print("✓ Audio file is available")
                                return True
                            else:
                                print(f"✗ Audio file not accessible: {audio_response.status_code}")
                                return False
                                
                        elif state == 'FAILURE':
                            error = status_data.get('error', 'Unknown error')
                            print(f"✗ Processing failed: {error}")
                            return False
                        
                        time.sleep(2)
                        attempt += 1
                    else:
                        print(f"✗ Status check failed: {status_response.status_code}")
                        return False
                        
                except Exception as e:
                    print(f"✗ Status check error: {e}")
                    return False
            
            print("✗ Processing timed out")
            return False
            
        else:
            print(f"✗ Upload failed: {response.status_code}")
            if response.headers.get('content-type', '').startswith('application/json'):
                error_data = response.json()
                print(f"  Error: {error_data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"✗ Upload error: {e}")
        return False
    finally:
        # Clean up test file
        if test_file.exists():
            test_file.unlink()

def test_invalid_requests():
    """Test error handling with invalid requests"""
    print("Testing error handling...")
    
    # Test upload without file
    try:
        response = requests.post(f"{API_BASE}/upload", timeout=10)
        if response.status_code == 400:
            print("✓ Correctly rejected upload without file")
        else:
            print(f"✗ Unexpected response for no file: {response.status_code}")
    except Exception as e:
        print(f"✗ Error testing no file upload: {e}")
    
    # Test status with invalid task ID
    try:
        response = requests.get(f"{API_BASE}/status/invalid-task-id", timeout=10)
        if response.status_code in [404, 400]:
            print("✓ Correctly handled invalid task ID")
        else:
            print(f"✗ Unexpected response for invalid task ID: {response.status_code}")
    except Exception as e:
        print(f"✗ Error testing invalid task ID: {e}")
    
    # Test audio with invalid task ID
    try:
        response = requests.get(f"{API_BASE}/audio/invalid-task-id", timeout=10)
        if response.status_code == 404:
            print("✓ Correctly handled invalid audio request")
        else:
            print(f"✗ Unexpected response for invalid audio: {response.status_code}")
    except Exception as e:
        print(f"✗ Error testing invalid audio request: {e}")

def main():
    """Run all tests"""
    print("PDF2Audio API Test Suite")
    print("=" * 40)
    
    tests = [
        ("Health Check", test_health),
        ("Voices Endpoint", test_voices),
        ("Error Handling", test_invalid_requests),
        # ("Upload and Process", test_upload_and_process),  # Commented out for quick testing
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * len(test_name))
        if test_func():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())