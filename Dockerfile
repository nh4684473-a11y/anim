# Root Dockerfile for easy deployment on Render (if Root Directory is not set)
FROM python:3.9-slim

WORKDIR /code

# Copy requirements from backend directory
COPY backend/requirements.txt /code/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the backend application code
COPY backend/app /code/app

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Set python path
ENV PYTHONPATH=/code

# Run the application using the PORT environment variable provided by Render
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
