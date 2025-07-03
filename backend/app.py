import os
import uuid
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS
from celery import Celery
from werkzeug.utils import secure_filename
import magic

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', '/app/uploads')
app.config['TEMP_FOLDER'] = os.environ.get('TEMP_FOLDER', '/app/temp')

# Enable CORS for all routes
CORS(app, origins=['http://localhost:12000', 'https://work-1-yynvnckwdflsxwor.prod-runtime.all-hands.dev'])

# Configure Celery
celery_broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
celery_result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

celery = Celery(
    app.import_name,
    broker=celery_broker_url,
    backend=celery_result_backend
)

# Update Celery configuration
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Ensure upload and temp directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_pdf(file_path):
    """Validate that the uploaded file is actually a PDF"""
    try:
        mime = magic.Magic(mime=True)
        file_type = mime.from_file(file_path)
        return file_type == 'application/pdf'
    except Exception as e:
        logger.error(f"Error validating PDF: {e}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            'grobid': os.environ.get('GROBID_URL', 'http://grobid:8070'),
            'piper': os.environ.get('PIPER_URL', 'http://piper:8080'),
            'redis': celery_broker_url
        }
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload PDF file and start processing"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only PDF files are allowed.'}), 400
        
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Secure filename and save
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{task_id}_{filename}")
        file.save(file_path)
        
        # Validate PDF
        if not validate_pdf(file_path):
            os.remove(file_path)
            return jsonify({'error': 'Invalid PDF file'}), 400
        
        # Get processing options from request
        voice_settings = {
            'language': request.form.get('language', 'en'),
            'voice': request.form.get('voice', 'default'),
            'speed': float(request.form.get('speed', 1.0))
        }
        
        # Start background processing
        from tasks import process_pdf_to_audio
        task = process_pdf_to_audio.delay(task_id, file_path, voice_settings)
        
        return jsonify({
            'task_id': task_id,
            'status': 'started',
            'message': 'PDF processing started'
        }), 202
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Get processing status for a task"""
    try:
        # Validate task_id format (should be UUID)
        try:
            uuid.UUID(task_id)
        except ValueError:
            return jsonify({'error': 'Invalid task ID format'}), 400
        
        from tasks import process_pdf_to_audio
        task = process_pdf_to_audio.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            # For invalid task IDs, Celery returns PENDING but with no info
            # We can check if this is a real pending task or invalid ID
            response = {
                'task_id': task_id,
                'state': task.state,
                'stage': 'queued',
                'progress': 0,
                'message': 'Task is waiting to be processed'
            }
        elif task.state == 'PROGRESS':
            response = {
                'task_id': task_id,
                'state': task.state,
                'stage': task.info.get('stage', 'processing'),
                'progress': task.info.get('progress', 0),
                'message': task.info.get('message', 'Processing...')
            }
        elif task.state == 'SUCCESS':
            response = {
                'task_id': task_id,
                'state': task.state,
                'stage': 'completed',
                'progress': 100,
                'message': 'Processing completed successfully',
                'result': task.result
            }
        else:  # FAILURE
            response = {
                'task_id': task_id,
                'state': task.state,
                'stage': 'failed',
                'progress': 0,
                'message': str(task.info),
                'error': str(task.info)
            }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/audio/<task_id>', methods=['GET'])
def get_audio(task_id):
    """Stream or download the generated audio file"""
    try:
        audio_path = os.path.join(app.config['TEMP_FOLDER'], f"{task_id}_audio.wav")
        
        if not os.path.exists(audio_path):
            return jsonify({'error': 'Audio file not found'}), 404
        
        # Check if file is too old (24 hours)
        file_age = datetime.now() - datetime.fromtimestamp(os.path.getctime(audio_path))
        if file_age > timedelta(hours=24):
            os.remove(audio_path)
            return jsonify({'error': 'Audio file has expired'}), 410
        
        download = request.args.get('download', 'false').lower() == 'true'
        
        return send_file(
            audio_path,
            as_attachment=download,
            download_name=f"audio_{task_id}.wav",
            mimetype='audio/wav'
        )
        
    except Exception as e:
        logger.error(f"Audio retrieval error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/voices', methods=['GET'])
def get_available_voices():
    """Get list of available voices and languages"""
    try:
        # This would typically query the Piper service
        # For now, return a static list
        voices = {
            'en': [
                {'id': 'en_US-lessac-medium', 'name': 'Lessac (US English)', 'gender': 'male'},
                {'id': 'en_US-libritts-high', 'name': 'LibriTTS (US English)', 'gender': 'mixed'},
                {'id': 'en_GB-alan-medium', 'name': 'Alan (British English)', 'gender': 'male'}
            ],
            'es': [
                {'id': 'es_ES-mls-medium', 'name': 'MLS (Spanish)', 'gender': 'mixed'}
            ],
            'fr': [
                {'id': 'fr_FR-mls-medium', 'name': 'MLS (French)', 'gender': 'mixed'}
            ],
            'de': [
                {'id': 'de_DE-thorsten-medium', 'name': 'Thorsten (German)', 'gender': 'male'}
            ],
            'it': [
                {'id': 'it_IT-riccardo-medium', 'name': 'Riccardo (Italian)', 'gender': 'male'}
            ]
        }
        
        return jsonify({
            'voices': voices,
            'default_language': 'en',
            'default_voice': 'en_US-lessac-medium'
        })
        
    except Exception as e:
        logger.error(f"Voices retrieval error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 100MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)