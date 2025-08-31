#!/usr/bin/env python3
"""
LegalSense AI Backend Startup Script (Optimized)
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        sys.exit(1)
    logger.info(f"Python version: {sys.version}")

def install_dependencies():
    """Install required dependencies"""
    try:
        logger.info("Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        logger.info("Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        sys.exit(1)

def setup_directories():
    """Create necessary directories"""
    directories = ["uploads", "processed", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.info(f"Created directory: {directory}")

def download_nlp_models():
    """Download required NLP models"""
    try:
        logger.info("Downloading NLP models...")
        
        # Download spaCy model
        try:
            import spacy
            spacy.load("en_core_web_sm")
            logger.info("spaCy model already available")
        except OSError:
            logger.info("Downloading spaCy model...")
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)
        
        # Download NLTK data
        try:
            import nltk
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
            logger.info("NLTK data already available")
        except LookupError:
            logger.info("Downloading NLTK data...")
            subprocess.run([sys.executable, "-c", "import nltk; nltk.download('punkt'); nltk.download('stopwords')"], check=True)
        
        logger.info("NLP models downloaded successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to download NLP models: {e}")
        logger.warning("Continuing without some NLP models...")

def check_environment():
    """Check environment configuration"""
    logger.info("Checking environment...")
    
    # Check for Google API key
    google_key = os.getenv("GOOGLE_API_KEY")
    if not google_key:
        logger.warning("GOOGLE_API_KEY not set. Some features will use local models only.")
        logger.info("Get your API key from: https://makersuite.google.com/app/apikey")
    else:
        logger.info("Google Gemini API key found")
    
    # Check for required directories
    if not os.path.exists("uploads"):
        logger.info("Creating uploads directory")
        os.makedirs("uploads", exist_ok=True)
    
    if not os.path.exists("processed"):
        logger.info("Creating processed directory")
        os.makedirs("processed", exist_ok=True)

def start_server():
    """Start the FastAPI server"""
    try:
        logger.info("Starting LegalSense AI Backend (Optimized)...")
        logger.info("Server will be available at: http://localhost:8000")
        logger.info("API documentation at: http://localhost:8000/docs")
        logger.info("Model information at: http://localhost:8000/api/models/info")
        
        # Import and run the FastAPI app
        from main import app
        import uvicorn
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

def main():
    """Main startup function"""
    logger.info("=== LegalSense AI Backend Startup (Optimized) ===")
    logger.info("🚀 Optimized with Gemini 2.0 Flash - 85% fewer API calls!")
    
    # Check Python version
    check_python_version()
    
    # Setup directories
    setup_directories()
    
    # Check environment
    check_environment()
    
    # Install dependencies if requirements.txt exists
    if os.path.exists("requirements.txt"):
        install_dependencies()
    
    # Download NLP models
    download_nlp_models()
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()
