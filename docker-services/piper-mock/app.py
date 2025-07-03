import os
import time
import wave
import struct
import logging
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

TEMP_DIR = '/app/temp'
os.makedirs(TEMP_DIR, exist_ok=True)

def generate_mock_audio(text, output_path, duration_seconds=None):
    """Generate a mock audio file with sine wave"""
    if duration_seconds is None:
        # Estimate duration based on text length (roughly 150 words per minute)
        words = len(text.split())
        duration_seconds = max(2, words / 2.5)  # Minimum 2 seconds
    
    sample_rate = 22050
    num_samples = int(sample_rate * duration_seconds)
    
    # Generate a simple sine wave
    frequency = 440  # A4 note
    samples = []
    for i in range(num_samples):
        # Create a simple tone that fades in and out
        t = i / sample_rate
        amplitude = 0.3 * (1 - abs(2 * t / duration_seconds - 1))  # Triangle envelope
        sample = amplitude * 32767 * (
            0.5 * (1 + 0.5 * (t * frequency % 1)) +  # Sawtooth-like wave
            0.3 * (1 if (t * frequency * 2) % 1 > 0.5 else -1)  # Square wave component
        )
        samples.append(int(sample))
    
    # Write WAV file
    with wave.open(output_path, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        # Convert samples to bytes
        for sample in samples:
            wav_file.writeframes(struct.pack('<h', sample))
    
    return True

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'piper-mock',
        'available_voices': ['en_US-lessac-medium']
    })

@app.route('/voices', methods=['GET'])
def get_voices():
    """Get available voice models (mock)"""
    return jsonify({
        'voices': {
            'en_US-lessac-medium': {
                'model': 'mock-model.onnx',
                'config': 'mock-model.onnx.json',
                'language': 'en',
                'gender': 'male',
                'quality': 'medium'
            }
        }
    })

@app.route('/synthesize', methods=['POST'])
def synthesize_speech():
    """Synthesize speech from text (mock)"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required'}), 400
        
        text = data['text']
        voice = data.get('voice', 'en_US-lessac-medium')
        speed = data.get('speed', 1.0)
        
        logger.info(f"Mock TTS request: {len(text)} characters, voice: {voice}, speed: {speed}")
        
        # Simulate processing time
        time.sleep(1)
        
        # Generate mock audio file
        output_path = os.path.join(TEMP_DIR, f"mock_audio_{int(time.time())}.wav")
        
        if generate_mock_audio(text, output_path):
            return send_file(
                output_path,
                mimetype='audio/wav',
                as_attachment=False
            )
        else:
            return jsonify({'error': 'Audio generation failed'}), 500
            
    except Exception as e:
        logger.error(f"Mock synthesis error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/synthesize_file', methods=['POST'])
def synthesize_to_file():
    """Synthesize speech and save to file (mock)"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required'}), 400
        
        text = data['text']
        voice = data.get('voice', 'en_US-lessac-medium')
        output_path = data.get('output_path')
        
        if not output_path:
            return jsonify({'error': 'Output path is required'}), 400
        
        logger.info(f"Mock TTS file request: {len(text)} characters, output: {output_path}")
        
        # Simulate processing time
        time.sleep(2)
        
        # Generate mock audio
        if generate_mock_audio(text, output_path):
            return jsonify({
                'success': True,
                'output_path': output_path,
                'voice_used': voice,
                'text_length': len(text),
                'mock': True
            })
        else:
            return jsonify({'error': 'Audio generation failed'}), 500
            
    except Exception as e:
        logger.error(f"Mock file synthesis error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting Piper TTS Mock Service")
    app.run(host='0.0.0.0', port=8080, debug=True)