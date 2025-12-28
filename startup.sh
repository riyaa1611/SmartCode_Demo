#!/bin/bash

# Startup script for Smart Code Review Bot

# Initialize database
echo "Initializing database..."
python init_db.py

# Start the web server
echo "Starting web server..."
uvicorn main:app --host 0.0.0.0 --port 8084 &

# Start the Celery worker
echo "Starting Celery worker..."
celery -A worker.celery_app worker --loglevel=info &

echo "Smart Code Review Bot is running!"
echo "Web API: http://localhost:8000"