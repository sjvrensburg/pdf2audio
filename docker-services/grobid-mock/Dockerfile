FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install flask flask-cors lxml

# Copy mock service
COPY app.py .

EXPOSE 8070

CMD ["python", "app.py"]