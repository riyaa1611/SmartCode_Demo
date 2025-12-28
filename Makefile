# Makefile for Smart Code Review Bot

.PHONY: install run dev test db-init worker

# Install dependencies
install:
	pip install -r requirements.txt

# Run the application
run:
	python run_app.py --port 8084

# Run the application in development mode
dev:
	python run_app.py --port 8084 --reload

# Run tests
test:
	python -m pytest tests/

# Initialize the database
db-init:
	python init_db.py

# Run the Celery worker
worker:
	celery -A worker.celery_app worker --loglevel=info

# Start all services with docker-compose
docker-up:
	docker-compose up -d

# Stop all services
docker-down:
	docker-compose down

# Build docker images
docker-build:
	docker-compose build