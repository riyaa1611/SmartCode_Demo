"""Test script to verify the setup"""

def test_imports():
    """Test that all required packages can be imported"""
    try:
        import fastapi
        print("✓ FastAPI imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import FastAPI: {e}")
        
    try:
        import uvicorn
        print("✓ Uvicorn imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Uvicorn: {e}")
        
    try:
        import github
        print("✓ PyGithub imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import PyGithub: {e}")
        
    try:
        import sqlalchemy
        print("✓ SQLAlchemy imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import SQLAlchemy: {e}")
        
    try:
        import celery
        print("✓ Celery imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Celery: {e}")
        
    try:
        import openai
        print("✓ OpenAI imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import OpenAI: {e}")
        
    try:
        import redis
        print("✓ Redis imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Redis: {e}")

if __name__ == "__main__":
    test_imports()