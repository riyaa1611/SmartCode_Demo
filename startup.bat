@echo off
REM Startup script for Smart Code Review Bot on Windows

REM Initialize database
echo Initializing database...
python init_db.py

REM Start the web server
echo Starting web server...
start "Web Server" uvicorn main:app --host 0.0.0.0 --port 8084

REM Start the Celery worker
echo Starting Celery worker...
start "Celery Worker" celery -A worker.celery_app worker --loglevel=info

echo Smart Code Review Bot is running!
echo Web API: http://localhost:8000