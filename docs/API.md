# PDF2Audio API Documentation

This document describes the REST API endpoints for the PDF2Audio service.

## Base URL

```
http://localhost:5000
```

## Authentication

No authentication is required. The API is designed for local use and temporary file processing.

## Rate Limiting

- Maximum file size: 100MB
- Concurrent uploads: Limited by system resources
- File retention: 24 hours

## Endpoints

### Health Check

Check the health status of all services.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "grobid": "http://grobid:8070",
    "piper": "http://piper:8080",
    "redis": "redis://redis:6379/0"
  }
}
```

**Status Codes:**
- `200`: All services healthy
- `503`: One or more services unavailable

---

### Upload PDF

Upload a PDF file for processing.

**Endpoint:** `POST /upload`

**Content-Type:** `multipart/form-data`

**Parameters:**
- `file` (required): PDF file to process
- `language` (optional): Target language code (default: "en")
- `voice` (optional): Voice model ID (default: "en_US-lessac-medium")
- `speed` (optional): Speech speed multiplier (default: 1.0, range: 0.5-2.0)

**Example Request:**
```bash
curl -X POST \
  -F "file=@document.pdf" \
  -F "language=en" \
  -F "voice=en_US-lessac-medium" \
  -F "speed=1.2" \
  http://localhost:5000/upload
```

**Response:**
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "started",
  "message": "PDF processing started"
}
```

**Status Codes:**
- `202`: Processing started successfully
- `400`: Invalid file or parameters
- `413`: File too large
- `500`: Server error

**Error Response:**
```json
{
  "error": "Invalid file type. Only PDF files are allowed."
}
```

---

### Get Task Status

Check the processing status of an uploaded file.

**Endpoint:** `GET /status/{task_id}`

**Parameters:**
- `task_id`: UUID returned from upload endpoint

**Example Request:**
```bash
curl http://localhost:5000/status/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Response (Processing):**
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "state": "PROGRESS",
  "stage": "extracting",
  "progress": 45,
  "message": "Extracting text and mathematics..."
}
```

**Response (Completed):**
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "state": "SUCCESS",
  "stage": "completed",
  "progress": 100,
  "message": "Processing completed successfully",
  "result": {
    "audio_url": "/audio/a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "text_length": 15420,
    "processing_time": 1642234567.89,
    "voice_used": "en_US-lessac-medium"
  }
}
```

**Response (Failed):**
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "state": "FAILURE",
  "stage": "failed",
  "progress": 0,
  "message": "Text extraction failed",
  "error": "GROBID service unavailable"
}
```

**Processing Stages:**
- `queued`: Task waiting to be processed
- `analyzing`: PDF structure analysis
- `extracting`: Text and math extraction
- `ocr_fallback`: Using OCR for image-based PDFs
- `processing`: Content preparation for TTS
- `synthesizing`: Audio generation
- `completed`: Processing finished
- `failed`: Error occurred

**Status Codes:**
- `200`: Status retrieved successfully
- `404`: Task not found
- `500`: Server error

---

### Get Audio File

Download or stream the generated audio file.

**Endpoint:** `GET /audio/{task_id}`

**Parameters:**
- `task_id`: UUID from upload response
- `download` (optional): Set to "true" to force download

**Example Requests:**
```bash
# Stream audio
curl http://localhost:5000/audio/a1b2c3d4-e5f6-7890-abcd-ef1234567890

# Download audio
curl -O http://localhost:5000/audio/a1b2c3d4-e5f6-7890-abcd-ef1234567890?download=true
```

**Response:**
- Content-Type: `audio/wav`
- Content-Disposition: `attachment` (if download=true)

**Status Codes:**
- `200`: Audio file returned
- `404`: Audio file not found
- `410`: Audio file expired (>24 hours old)
- `500`: Server error

---

### Get Available Voices

Retrieve list of available voice models and languages.

**Endpoint:** `GET /voices`

**Example Request:**
```bash
curl http://localhost:5000/voices
```

**Response:**
```json
{
  "voices": {
    "en": [
      {
        "id": "en_US-lessac-medium",
        "name": "Lessac (US English)",
        "gender": "male"
      },
      {
        "id": "en_US-libritts-high",
        "name": "LibriTTS (US English)",
        "gender": "mixed"
      },
      {
        "id": "en_GB-alan-medium",
        "name": "Alan (British English)",
        "gender": "male"
      }
    ],
    "es": [
      {
        "id": "es_ES-mls-medium",
        "name": "MLS (Spanish)",
        "gender": "mixed"
      }
    ],
    "fr": [
      {
        "id": "fr_FR-mls-medium",
        "name": "MLS (French)",
        "gender": "mixed"
      }
    ]
  },
  "default_language": "en",
  "default_voice": "en_US-lessac-medium"
}
```

**Status Codes:**
- `200`: Voices retrieved successfully
- `500`: Server error

---

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Human-readable error message"
}
```

Common error scenarios:

### File Upload Errors
- **Invalid file type**: Only PDF files are accepted
- **File too large**: Maximum 100MB file size
- **Corrupted PDF**: File cannot be read as valid PDF
- **No file provided**: Request missing file parameter

### Processing Errors
- **GROBID unavailable**: PDF parsing service down
- **Piper TTS unavailable**: Speech synthesis service down
- **Text extraction failed**: Unable to extract readable text
- **Audio generation failed**: TTS processing error

### Resource Errors
- **Disk space full**: Insufficient storage for processing
- **Memory limit exceeded**: Document too complex for available RAM
- **Processing timeout**: Operation exceeded time limit

## Rate Limiting

The API implements the following limits:

- **Concurrent uploads**: 5 per client IP
- **File size**: 100MB maximum
- **Processing time**: 30 minutes maximum
- **Storage**: Files deleted after 24 hours

## WebSocket Support

For real-time status updates, consider implementing WebSocket connections:

```javascript
const ws = new WebSocket('ws://localhost:5000/ws/status/' + taskId);
ws.onmessage = function(event) {
  const status = JSON.parse(event.data);
  console.log('Status update:', status);
};
```

*Note: WebSocket support is planned for future releases.*

## SDK Examples

### JavaScript/Node.js

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

class PDF2AudioClient {
  constructor(baseURL = 'http://localhost:5000') {
    this.baseURL = baseURL;
    this.client = axios.create({ baseURL });
  }

  async uploadPDF(filePath, options = {}) {
    const form = new FormData();
    form.append('file', fs.createReadStream(filePath));
    
    if (options.language) form.append('language', options.language);
    if (options.voice) form.append('voice', options.voice);
    if (options.speed) form.append('speed', options.speed.toString());

    const response = await this.client.post('/upload', form, {
      headers: form.getHeaders()
    });
    
    return response.data;
  }

  async getStatus(taskId) {
    const response = await this.client.get(`/status/${taskId}`);
    return response.data;
  }

  async waitForCompletion(taskId, pollInterval = 2000) {
    while (true) {
      const status = await this.getStatus(taskId);
      
      if (status.state === 'SUCCESS') {
        return status;
      } else if (status.state === 'FAILURE') {
        throw new Error(status.message);
      }
      
      await new Promise(resolve => setTimeout(resolve, pollInterval));
    }
  }

  getAudioURL(taskId, download = false) {
    const params = download ? '?download=true' : '';
    return `${this.baseURL}/audio/${taskId}${params}`;
  }
}

// Usage example
async function convertPDF() {
  const client = new PDF2AudioClient();
  
  try {
    // Upload PDF
    const upload = await client.uploadPDF('./document.pdf', {
      language: 'en',
      voice: 'en_US-lessac-medium',
      speed: 1.2
    });
    
    console.log('Upload started:', upload.task_id);
    
    // Wait for completion
    const result = await client.waitForCompletion(upload.task_id);
    console.log('Processing completed:', result);
    
    // Get audio URL
    const audioURL = client.getAudioURL(upload.task_id);
    console.log('Audio available at:', audioURL);
    
  } catch (error) {
    console.error('Error:', error.message);
  }
}
```

### Python

```python
import requests
import time
from pathlib import Path

class PDF2AudioClient:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        self.session = requests.Session()
    
    def upload_pdf(self, file_path, language='en', voice='en_US-lessac-medium', speed=1.0):
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'language': language,
                'voice': voice,
                'speed': str(speed)
            }
            
            response = self.session.post(f'{self.base_url}/upload', 
                                       files=files, data=data)
            response.raise_for_status()
            return response.json()
    
    def get_status(self, task_id):
        response = self.session.get(f'{self.base_url}/status/{task_id}')
        response.raise_for_status()
        return response.json()
    
    def wait_for_completion(self, task_id, poll_interval=2):
        while True:
            status = self.get_status(task_id)
            
            if status['state'] == 'SUCCESS':
                return status
            elif status['state'] == 'FAILURE':
                raise Exception(status['message'])
            
            time.sleep(poll_interval)
    
    def download_audio(self, task_id, output_path):
        response = self.session.get(f'{self.base_url}/audio/{task_id}?download=true')
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)

# Usage example
if __name__ == '__main__':
    client = PDF2AudioClient()
    
    try:
        # Upload PDF
        upload = client.upload_pdf('./document.pdf', 
                                 language='en', 
                                 voice='en_US-lessac-medium',
                                 speed=1.2)
        
        print(f"Upload started: {upload['task_id']}")
        
        # Wait for completion
        result = client.wait_for_completion(upload['task_id'])
        print(f"Processing completed: {result}")
        
        # Download audio
        client.download_audio(upload['task_id'], './output.wav')
        print("Audio downloaded to ./output.wav")
        
    except Exception as e:
        print(f"Error: {e}")
```

## Testing

Use the provided test scripts to validate API functionality:

```bash
# Test health endpoint
curl -f http://localhost:5000/health || echo "Health check failed"

# Test file upload with invalid file
curl -X POST -F "file=@test.txt" http://localhost:5000/upload

# Test status with invalid task ID
curl http://localhost:5000/status/invalid-task-id
```

For comprehensive API testing, see the test suite in `/tests/api/`.