# 🚀 PDF2Audio Deployment Guide

## 📦 Creating a GitHub Repository

### Option 1: Manual GitHub Repository Creation

1. **Go to GitHub** and create a new repository:
   - Repository name: `pdf2audio`
   - Description: `🎧 Dockerized web application that converts academic PDFs with mathematical content into natural-sounding audio using open-source tools`
   - Make it public
   - Don't initialize with README (we already have one)

2. **Push your local repository:**
```bash
cd /workspace/pdf2audio
git remote add origin https://github.com/YOUR_USERNAME/pdf2audio.git
git push -u origin main
```

### Option 2: Using GitHub CLI (if available)

```bash
# Install GitHub CLI if not available
# Then create and push
gh repo create pdf2audio --public --description "🎧 Dockerized web application that converts academic PDFs with mathematical content into natural-sounding audio using open-source tools"
git remote add origin https://github.com/YOUR_USERNAME/pdf2audio.git
git push -u origin main
```

## 📁 Download the Application

### Method 1: Direct Download from GitHub
Once the repository is created, users can:
```bash
git clone https://github.com/YOUR_USERNAME/pdf2audio.git
cd pdf2audio
./setup.sh
```

### Method 2: Download as ZIP
1. Go to your GitHub repository
2. Click "Code" → "Download ZIP"
3. Extract the ZIP file
4. Run the setup script

### Method 3: Fork the Repository
Users can fork your repository to their own GitHub account and then clone their fork.

## 🌐 Deployment Options

### Local Development
```bash
git clone https://github.com/YOUR_USERNAME/pdf2audio.git
cd pdf2audio
./setup.sh
docker compose -f docker-compose.dev.yml up --build
```

### Production Deployment
```bash
git clone https://github.com/YOUR_USERNAME/pdf2audio.git
cd pdf2audio
./setup.sh
docker compose up --build -d
```

### Cloud Deployment

#### AWS EC2
1. Launch an EC2 instance (t3.large or larger recommended)
2. Install Docker and Docker Compose
3. Clone the repository and run setup
4. Configure security groups for ports 12000 and 5000
5. Start the application

#### Google Cloud Platform
1. Create a Compute Engine instance
2. Install Docker and Docker Compose
3. Clone and setup the application
4. Configure firewall rules

#### DigitalOcean Droplet
1. Create a droplet with Docker pre-installed
2. Clone the repository
3. Run the setup and start services

## 🔧 Environment Configuration

### Production Environment Variables
Create a `.env` file for production:
```env
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# File Upload Configuration
MAX_CONTENT_LENGTH=104857600  # 100MB
UPLOAD_FOLDER=/app/uploads

# TTS Configuration
DEFAULT_LANGUAGE=en
DEFAULT_VOICE=en_US-lessac-medium

# Cleanup Configuration
CLEANUP_INTERVAL_HOURS=24
```

### SSL/HTTPS Setup
For production, consider using:
- Nginx reverse proxy with SSL certificates
- Let's Encrypt for free SSL certificates
- Cloudflare for CDN and SSL

## 📊 Monitoring and Logging

### Health Checks
The application provides health check endpoints:
- Backend: `http://localhost:5000/health`
- GROBID: `http://localhost:8070/health`
- Piper TTS: `http://localhost:8080/health`

### Logging
View application logs:
```bash
docker compose logs -f backend
docker compose logs -f celery-worker
docker compose logs -f frontend
```

### Resource Monitoring
Monitor resource usage:
```bash
docker stats
```

## 🔒 Security Considerations

### Production Security
1. **Change default secrets** in production
2. **Use HTTPS** for all communications
3. **Implement rate limiting** for API endpoints
4. **Regular security updates** for base images
5. **File upload validation** and scanning
6. **Network isolation** between services

### Firewall Configuration
Only expose necessary ports:
- Port 12000: Frontend (HTTPS recommended)
- Port 5000: Backend API (internal only, behind reverse proxy)

## 📈 Scaling

### Horizontal Scaling
- Multiple Celery workers for processing
- Load balancer for frontend instances
- Redis cluster for high availability

### Vertical Scaling
- Increase memory for GROBID processing
- More CPU cores for TTS synthesis
- SSD storage for faster I/O

## 🛠 Maintenance

### Regular Tasks
1. **Update base images** monthly
2. **Clean up old files** (automated)
3. **Monitor disk usage**
4. **Check service health**
5. **Update dependencies**

### Backup Strategy
- Configuration files
- Custom voice models (if any)
- Application logs
- Docker volumes

## 📞 Support

### Troubleshooting
1. Check service health endpoints
2. Review Docker logs
3. Verify file permissions
4. Check available disk space
5. Monitor memory usage

### Common Issues
- **Out of memory**: Increase Docker memory limits
- **Slow processing**: Add more Celery workers
- **File upload fails**: Check file size limits
- **Audio generation fails**: Verify Piper TTS service

## 🎯 Performance Optimization

### Recommended Specifications
- **Minimum**: 4GB RAM, 2 CPU cores, 20GB storage
- **Recommended**: 8GB RAM, 4 CPU cores, 50GB storage
- **High-load**: 16GB RAM, 8 CPU cores, 100GB storage

### Optimization Tips
1. Use SSD storage for better I/O
2. Increase Celery worker count for parallel processing
3. Configure Redis memory limits
4. Use CDN for static assets
5. Implement caching for frequently accessed files