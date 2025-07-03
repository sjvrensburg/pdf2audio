# PDF2Audio - Academic PDF to Speech Converter

A Dockerized web application that converts academic PDFs with mathematical content into natural-sounding audio using only open-source tools. Designed for accessibility and ease of use by researchers and students.

## 🚀 Features

- **Smart PDF Processing**: Uses GROBID v0.8.0 for accurate text and mathematical formula extraction
- **Mathematical Speech**: MathJax Speech Rule Engine converts mathematical expressions to spoken text
- **High-Quality TTS**: Piper TTS provides natural-sounding speech synthesis in multiple languages
- **Accessible UI**: WCAG 2.1 AA compliant React frontend with keyboard navigation and screen reader support
- **Multiple Languages**: Support for English, Spanish, French, German, and Italian
- **Customizable Voices**: Choose from different voice models and adjust speech speed
- **Privacy-First**: Files automatically deleted after 24 hours, no persistent user data
- **Offline Capable**: Runs entirely in Docker containers without external dependencies

## 🛠 Technology Stack

### Backend
- **Flask + Celery + Redis**: Async processing pipeline
- **GROBID**: PDF parsing and TEI/MathML extraction
- **MathJax SRE**: Mathematical expression to speech conversion
- **Piper TTS**: Neural text-to-speech synthesis
- **Tesseract OCR**: Fallback for image-based PDFs

### Frontend
- **React 18**: Modern UI framework
- **Tailwind CSS**: Utility-first styling
- **Headless UI**: Accessible components
- **Axios**: HTTP client for API communication

### Infrastructure
- **Docker Compose**: Multi-service orchestration
- **Redis**: Task queue and caching
- **Nginx**: (Optional) Reverse proxy and static file serving

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 8GB+ RAM (recommended for GROBID)
- 10GB+ disk space for models and temporary files

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/YOUR_USERNAME/pdf2audio.git
cd pdf2audio

# Run setup script to clone required dependencies
./setup.sh
```

### 2. Start Services

**For Development (with mock services):**
```bash
docker compose -f docker-compose.dev.yml up --build -d
```

**For Production (with real services):**
```bash
docker compose up --build -d
```

**View logs:**
```bash
docker compose logs -f
```

### 3. Access Application

- **Frontend**: http://localhost:12000
- **Backend API**: http://localhost:5000
- **GROBID**: http://localhost:8070
- **Piper TTS**: http://localhost:8080

### 4. Health Check

```bash
# Check all services are running
curl http://localhost:5000/health
```

## 📖 Usage

### Web Interface

1. **Upload PDF**: Drag and drop or click to select a PDF file (max 100MB)
2. **Configure Voice**: Choose language, voice model, and speech speed
3. **Process**: Wait for the 5-stage processing pipeline to complete
4. **Listen**: Use the built-in audio player or download the WAV file

### Processing Stages

1. **Analyzing**: PDF structure analysis and validation
2. **Extracting**: Text and mathematical content extraction via GROBID
3. **Processing**: Content cleaning and MathML to speech conversion
4. **Synthesizing**: Audio generation using Piper TTS
5. **Completed**: Audio ready for playback and download

### API Usage

See [API.md](docs/API.md) for detailed endpoint documentation.

## 🔧 Configuration

### Environment Variables

Create a `.env` file to customize settings:

```bash
# Backend Configuration
FLASK_ENV=production
CELERY_BROKER_URL=redis://redis:6379/0
GROBID_URL=http://grobid:8070
PIPER_URL=http://piper:8080

# File Management
UPLOAD_FOLDER=/app/uploads
TEMP_FOLDER=/app/temp
MAX_FILE_SIZE=104857600  # 100MB

# Cleanup Service
CLEANUP_INTERVAL=3600    # 1 hour
TTL_HOURS=24            # 24 hours

# Frontend
REACT_APP_API_URL=http://localhost:5000
```

### Voice Models

The application includes English voice models by default. To add more languages:

1. Download voice models from [Piper Voices](https://huggingface.co/rhasspy/piper-voices)
2. Place `.onnx` and `.onnx.json` files in `docker-services/piper-service/models/`
3. Update `AVAILABLE_VOICES` in `docker-services/piper-service/app.py`
4. Rebuild the Piper service: `docker-compose build piper`

## 🧪 Testing

### Manual Testing

Test with the provided sample documents:

```bash
# Download test PDFs
mkdir -p tests/samples
cd tests/samples

# ArXiv paper (math-heavy)
wget https://arxiv.org/pdf/2301.00001.pdf -O arxiv-paper.pdf

# Process via API
curl -X POST -F "file=@arxiv-paper.pdf" \
  -F "language=en" -F "voice=en_US-lessac-medium" \
  http://localhost:5000/upload
```

### Performance Benchmarks

Expected processing times on modern hardware:

| Document Type | Pages | Processing Time | Success Rate |
|---------------|-------|-----------------|--------------|
| Text PDF      | 10    | 2-4 minutes     | 95%+         |
| Math-heavy    | 20    | 4-8 minutes     | 90%+         |
| Scanned PDF   | 10    | 6-12 minutes    | 80%+         |

### Accessibility Testing

```bash
# Install axe-core CLI
npm install -g @axe-core/cli

# Run accessibility audit
axe http://localhost:12000 --tags wcag2a,wcag2aa
```

## 🔍 Troubleshooting

### Common Issues

**GROBID Service Fails to Start**
```bash
# Check memory allocation
docker stats grobid
# Increase memory limit in docker-compose.yml
```

**Audio Generation Fails**
```bash
# Check Piper service logs
docker-compose logs piper
# Verify voice models are downloaded
docker-compose exec piper ls -la /app/models/
```

**Frontend Can't Connect to Backend**
```bash
# Check network connectivity
docker-compose exec frontend curl http://backend:5000/health
# Verify CORS configuration
```

### Log Analysis

```bash
# View all service logs
docker-compose logs

# Follow specific service
docker-compose logs -f backend

# Check Celery worker status
docker-compose exec celery-worker celery -A app.celery inspect active
```

## 📊 Monitoring

### Service Health

```bash
# Check all services
curl http://localhost:5000/health

# Redis status
docker-compose exec redis redis-cli ping

# GROBID status
curl http://localhost:8070/api/isalive
```

### Resource Usage

```bash
# Monitor container resources
docker stats

# Check disk usage
docker system df
```

## 🔒 Security Considerations

- Files are automatically deleted after 24 hours
- No persistent user data storage
- Input validation for file types and sizes
- CORS protection for API endpoints
- No external network dependencies in production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Submit a pull request with detailed description

### Development Setup

```bash
# Start in development mode
docker-compose -f docker-compose.dev.yml up

# Run frontend in development
cd frontend && npm start

# Run backend tests
cd backend && python -m pytest
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [GROBID](https://github.com/kermitt2/grobid) - PDF parsing and scholarly document analysis
- [MathJax Speech Rule Engine](https://github.com/zorkow/speech-rule-engine) - Mathematical expression to speech
- [Piper TTS](https://github.com/rhasspy/piper) - Neural text-to-speech synthesis
- [React](https://reactjs.org/) - Frontend framework
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework

## 📞 Support

For issues and questions:

1. Check the [troubleshooting section](#-troubleshooting)
2. Search existing [GitHub issues](https://github.com/your-repo/issues)
3. Create a new issue with detailed information

---

**Note**: This application is designed for academic and research purposes. Processing times may vary based on document complexity and system resources.