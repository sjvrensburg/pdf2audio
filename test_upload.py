#!/usr/bin/env python3
"""
Test file upload and processing
"""

import requests
import time
import json

def test_upload():
    """Test uploading a text file as PDF (for testing)"""
    
    # Create a simple test content
    test_content = """
    Test Document for PDF2Audio

    This is a test document to verify the PDF2Audio conversion system.

    Mathematical Content:
    - Simple equation: E = mc²
    - Fraction: 1/2 + 3/4 = 5/4
    - Square root: √16 = 4
    - Integral: ∫ x dx = x²/2 + C

    Regular Text:
    This document contains both regular text and mathematical notation
    to test the complete processing pipeline.
    """
    
    # Create a test file
    with open('test_document.txt', 'w') as f:
        f.write(test_content)
    
    # Upload the file
    try:
        with open('test_document.txt', 'rb') as f:
            files = {'file': ('test_document.pdf', f, 'application/pdf')}
            data = {
                'language': 'en',
                'voice': 'en_US-lessac-medium',
                'speed': '1.0'
            }
            
            print("Uploading test file...")
            response = requests.post('http://localhost:5000/upload', files=files, data=data)
            
            if response.status_code == 202:
                result = response.json()
                task_id = result['task_id']
                print(f"✓ Upload successful! Task ID: {task_id}")
                
                # Monitor progress
                print("\nMonitoring progress:")
                print("-" * 50)
                
                while True:
                    status_response = requests.get(f'http://localhost:5000/status/{task_id}')
                    if status_response.status_code == 200:
                        status = status_response.json()
                        state = status.get('state', 'UNKNOWN')
                        stage = status.get('stage', 'unknown')
                        progress = status.get('progress', 0)
                        message = status.get('message', '')
                        
                        print(f"[{state}] {stage}: {progress}% - {message}")
                        
                        if state == 'SUCCESS':
                            print("\n✓ Processing completed successfully!")
                            print(f"Result: {json.dumps(status.get('result', {}), indent=2)}")
                            
                            # Test audio endpoint
                            audio_url = f'http://localhost:5000/audio/{task_id}'
                            audio_response = requests.head(audio_url)
                            if audio_response.status_code == 200:
                                print(f"✓ Audio file available at: {audio_url}")
                            else:
                                print(f"✗ Audio file not available: {audio_response.status_code}")
                            break
                            
                        elif state == 'FAILURE':
                            print(f"\n✗ Processing failed: {status.get('error', 'Unknown error')}")
                            break
                        
                        time.sleep(2)
                    else:
                        print(f"✗ Status check failed: {status_response.status_code}")
                        break
                        
            else:
                print(f"✗ Upload failed: {response.status_code}")
                if response.headers.get('content-type', '').startswith('application/json'):
                    error = response.json()
                    print(f"Error: {error.get('error', 'Unknown error')}")
                else:
                    print(f"Response: {response.text}")
                    
    except Exception as e:
        print(f"✗ Error: {e}")
    
    finally:
        # Clean up
        import os
        if os.path.exists('test_document.txt'):
            os.remove('test_document.txt')

if __name__ == '__main__':
    test_upload()