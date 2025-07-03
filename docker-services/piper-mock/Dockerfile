FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install flask flask-cors

# Copy mock service
COPY app.py .

# Create temp directory
RUN mkdir -p temp

EXPOSE 8080

CMD ["python", "app.py"]