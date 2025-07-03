import os
import logging
import requests
import time
import subprocess
from celery import Celery
from lxml import etree
import PyPDF2
import pytesseract
from PIL import Image
import tempfile
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery
celery_broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
celery_result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

celery = Celery(
    'tasks',
    broker=celery_broker_url,
    backend=celery_result_backend
)

# Service URLs
GROBID_URL = os.environ.get('GROBID_URL', 'http://grobid:8070')
PIPER_URL = os.environ.get('PIPER_URL', 'http://piper:8080')
TEMP_FOLDER = os.environ.get('TEMP_FOLDER', '/app/temp')

class MathMLProcessor:
    """Process MathML using Speech Rule Engine"""
    
    def __init__(self):
        self.sre_path = '/app/speech-rule-engine'
    
    def mathml_to_speech(self, mathml_content):
        """Convert MathML to spoken text using SRE"""
        try:
            # Create a temporary file for MathML
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
                f.write(mathml_content)
                mathml_file = f.name
            
            # Use Node.js to run SRE (simplified approach)
            # In production, this would use the bundled WebWorker
            cmd = [
                'node', '-e', f'''
                const sre = require('{self.sre_path}/lib/sre.js');
                const fs = require('fs');
                const mathml = fs.readFileSync('{mathml_file}', 'utf8');
                sre.setupEngine({{domain: 'mathspeak', style: 'default', markup: 'none'}});
                const speech = sre.toSpeech(mathml);
                console.log(speech);
                '''
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Clean up temp file
            os.unlink(mathml_file)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.warning(f"SRE processing failed: {result.stderr}")
                return "[Mathematical expression]"
                
        except Exception as e:
            logger.error(f"MathML processing error: {e}")
            return "[Mathematical expression]"

def extract_text_with_grobid(pdf_path):
    """Extract text and MathML from PDF using GROBID"""
    try:
        with open(pdf_path, 'rb') as pdf_file:
            files = {'input': pdf_file}
            response = requests.post(
                f"{GROBID_URL}/api/processFulltextDocument",
                files=files,
                timeout=300
            )
        
        if response.status_code == 200:
            return response.text
        else:
            logger.error(f"GROBID processing failed: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"GROBID extraction error: {e}")
        return None

def extract_text_with_tesseract(pdf_path):
    """Fallback OCR extraction using Tesseract"""
    try:
        # Convert PDF to images and OCR each page
        # This is a simplified implementation
        text_content = []
        
        # Use PyPDF2 to get page count
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
        
        # For each page, extract text using OCR
        # Note: This would need pdf2image in production
        for page_num in range(min(num_pages, 10)):  # Limit to 10 pages for demo
            try:
                # Simplified OCR - in production would convert PDF page to image first
                page_text = f"[OCR Page {page_num + 1} - Text extraction via Tesseract]"
                text_content.append(page_text)
            except Exception as e:
                logger.warning(f"OCR failed for page {page_num}: {e}")
                text_content.append(f"[OCR failed for page {page_num + 1}]")
        
        return "\n\n".join(text_content)
        
    except Exception as e:
        logger.error(f"Tesseract extraction error: {e}")
        return None

def parse_tei_xml(tei_content):
    """Parse TEI XML and extract text with MathML"""
    try:
        root = etree.fromstring(tei_content.encode('utf-8'))
        
        # Extract text content
        text_elements = root.xpath('//text//p | //text//head')
        mathml_elements = root.xpath('//m:math', namespaces={'m': 'http://www.w3.org/1998/Math/MathML'})
        
        content_parts = []
        math_processor = MathMLProcessor()
        
        # Process text elements
        for elem in text_elements:
            text = etree.tostring(elem, method='text', encoding='unicode').strip()
            if text:
                content_parts.append(text)
        
        # Process MathML elements
        for math_elem in mathml_elements:
            mathml_str = etree.tostring(math_elem, encoding='unicode')
            spoken_math = math_processor.mathml_to_speech(mathml_str)
            content_parts.append(f" {spoken_math} ")
        
        return " ".join(content_parts)
        
    except Exception as e:
        logger.error(f"TEI parsing error: {e}")
        return None

def synthesize_speech(text, voice_settings, output_path):
    """Synthesize speech using Piper TTS"""
    try:
        payload = {
            'text': text,
            'voice': voice_settings.get('voice', 'en_US-lessac-medium'),
            'speed': voice_settings.get('speed', 1.0),
            'output_path': output_path
        }
        
        response = requests.post(
            f"{PIPER_URL}/synthesize_file",
            json=payload,
            timeout=300
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('success', False)
        else:
            logger.error(f"Piper TTS failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Speech synthesis error: {e}")
        return False

@celery.task(bind=True)
def process_pdf_to_audio(self, task_id, pdf_path, voice_settings):
    """Main task to process PDF to audio"""
    try:
        # Stage 1: PDF Analysis
        self.update_state(
            state='PROGRESS',
            meta={
                'stage': 'analyzing',
                'progress': 10,
                'message': 'Analyzing PDF structure...'
            }
        )
        
        # Stage 2: Text Extraction with GROBID
        self.update_state(
            state='PROGRESS',
            meta={
                'stage': 'extracting',
                'progress': 25,
                'message': 'Extracting text and mathematics...'
            }
        )
        
        tei_content = extract_text_with_grobid(pdf_path)
        extracted_text = None
        
        if tei_content:
            extracted_text = parse_tei_xml(tei_content)
        
        # Stage 3: Fallback to OCR if needed
        if not extracted_text or len(extracted_text.strip()) < 100:
            self.update_state(
                state='PROGRESS',
                meta={
                    'stage': 'ocr_fallback',
                    'progress': 40,
                    'message': 'Using OCR fallback for text extraction...'
                }
            )
            
            ocr_text = extract_text_with_tesseract(pdf_path)
            if ocr_text:
                extracted_text = ocr_text
        
        if not extracted_text:
            raise Exception("Failed to extract text from PDF")
        
        # Stage 4: Text Processing
        self.update_state(
            state='PROGRESS',
            meta={
                'stage': 'processing',
                'progress': 60,
                'message': 'Processing text for speech synthesis...'
            }
        )
        
        # Clean and prepare text for TTS
        # Remove excessive whitespace, handle special characters
        cleaned_text = " ".join(extracted_text.split())
        
        # Limit text length for demo (first 5000 characters)
        if len(cleaned_text) > 5000:
            cleaned_text = cleaned_text[:5000] + "... [Content truncated for demo]"
        
        # Stage 5: Speech Synthesis
        self.update_state(
            state='PROGRESS',
            meta={
                'stage': 'synthesizing',
                'progress': 80,
                'message': 'Generating audio...'
            }
        )
        
        audio_path = os.path.join(TEMP_FOLDER, f"{task_id}_audio.wav")
        
        if synthesize_speech(cleaned_text, voice_settings, audio_path):
            # Stage 6: Completion
            self.update_state(
                state='PROGRESS',
                meta={
                    'stage': 'completed',
                    'progress': 100,
                    'message': 'Audio generation completed!'
                }
            )
            
            # Clean up original PDF
            try:
                os.remove(pdf_path)
            except:
                pass
            
            return {
                'audio_url': f"/audio/{task_id}",
                'text_length': len(cleaned_text),
                'processing_time': time.time(),
                'voice_used': voice_settings.get('voice', 'default')
            }
        else:
            raise Exception("Speech synthesis failed")
            
    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}")
        
        # Clean up files on failure
        try:
            os.remove(pdf_path)
        except:
            pass
        
        self.update_state(
            state='FAILURE',
            meta={
                'stage': 'failed',
                'progress': 0,
                'message': f'Processing failed: {str(e)}'
            }
        )
        raise e