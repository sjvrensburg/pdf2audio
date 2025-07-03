import os
import subprocess
import tempfile
import logging
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

PIPER_BINARY = '/app/piper'
MODELS_DIR = '/app/models'
TEMP_DIR = '/app/temp'

# Ensure temp directory exists
os.makedirs(TEMP_DIR, exist_ok=True)

# Available voice models
AVAILABLE_VOICES = {
    'en_US-lessac-medium': {
        'model': 'en_US-lessac-medium.onnx',
        'config': 'en_US-lessac-medium.onnx.json',
        'language': 'en',
        'gender': 'male',
        'quality': 'medium'
    }
}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'available_voices': list(AVAILABLE_VOICES.keys()),
        'piper_binary': os.path.exists(PIPER_BINARY)
    })

@app.route('/voices', methods=['GET'])
def get_voices():
    """Get available voice models"""
    return jsonify({
        'voices': AVAILABLE_VOICES
    })

@app.route('/synthesize', methods=['POST'])
def synthesize_speech():
    """Synthesize speech from text"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required'}), 400
        
        text = data['text']
        voice = data.get('voice', 'en_US-lessac-medium')
        speed = data.get('speed', 1.0)
        
        if voice not in AVAILABLE_VOICES:
            return jsonify({'error': f'Voice {voice} not available'}), 400
        
        # Prepare model paths
        voice_info = AVAILABLE_VOICES[voice]
        model_path = os.path.join(MODELS_DIR, voice_info['model'])
        config_path = os.path.join(MODELS_DIR, voice_info['config'])
        
        if not os.path.exists(model_path):
            return jsonify({'error': f'Model file not found: {voice_info["model"]}'}), 500
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as text_file:
            text_file.write(text)
            text_file_path = text_file.name
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as audio_file:
            audio_file_path = audio_file.name
        
        try:
            # Run Piper TTS
            cmd = [
                PIPER_BINARY,
                '--model', model_path,
                '--config', config_path,
                '--output_file', audio_file_path
            ]
            
            # Add speed control if supported
            if speed != 1.0:
                cmd.extend(['--length_scale', str(1.0 / speed)])
            
            # Run the command with text input
            with open(text_file_path, 'r') as input_file:
                result = subprocess.run(
                    cmd,
                    stdin=input_file,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
            
            if result.returncode != 0:
                logger.error(f"Piper failed: {result.stderr}")
                return jsonify({'error': 'Speech synthesis failed'}), 500
            
            # Return the audio file
            return send_file(
                audio_file_path,
                mimetype='audio/wav',
                as_attachment=False
            )
            
        finally:
            # Clean up temporary files
            try:
                os.unlink(text_file_path)
            except:
                pass
            
            # Note: audio file will be cleaned up by Flask after sending
            
    except Exception as e:
        logger.error(f"Synthesis error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/synthesize_file', methods=['POST'])
def synthesize_to_file():
    """Synthesize speech and return file path (for internal use)"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required'}), 400
        
        text = data['text']
        voice = data.get('voice', 'en_US-lessac-medium')
        output_path = data.get('output_path')
        
        if not output_path:
            return jsonify({'error': 'Output path is required'}), 400
        
        if voice not in AVAILABLE_VOICES:
            return jsonify({'error': f'Voice {voice} not available'}), 400
        
        # Prepare model paths
        voice_info = AVAILABLE_VOICES[voice]
        model_path = os.path.join(MODELS_DIR, voice_info['model'])
        
        # Create temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as text_file:
            text_file.write(text)
            text_file_path = text_file.name
        
        try:
            # Run Piper TTS
            cmd = [
                PIPER_BINARY,
                '--model', model_path,
                '--output_file', output_path
            ]
            
            with open(text_file_path, 'r') as input_file:
                result = subprocess.run(
                    cmd,
                    stdin=input_file,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
            
            if result.returncode != 0:
                logger.error(f"Piper failed: {result.stderr}")
                return jsonify({'error': 'Speech synthesis failed'}), 500
            
            return jsonify({
                'success': True,
                'output_path': output_path,
                'voice_used': voice
            })
            
        finally:
            # Clean up temporary text file
            try:
                os.unlink(text_file_path)
            except:
                pass
            
    except Exception as e:
        logger.error(f"File synthesis error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)