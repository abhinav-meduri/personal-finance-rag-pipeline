#!/usr/bin/env python3
"""
Setup Script for Bogleheads RAG Pipeline
Orchestrates the entire setup process from data preprocessing to vector database creation
"""

import os
import sys
from pathlib import Path
import logging
import subprocess
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_requirements():
    """Check if all required files exist"""
    required_files = [
        "mistral-7b-instruct-v0.1.Q4_K_M.gguf",
        "wiki_pages"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        logger.error(f"Missing required files: {missing_files}")
        logger.error("Please ensure you have:")
        logger.error("1. The Mistral-7b model file: mistral-7b-instruct-v0.1.Q4_K_M.gguf")
        logger.error("2. The wiki_pages directory with downloaded Bogleheads wiki pages")
        return False
    
    return True

def install_dependencies():
    """Install required Python packages"""
    logger.info("Installing Python dependencies...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True, text=True)
        logger.info("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False

def run_data_preprocessing():
    """Run the data preprocessing step"""
    logger.info("Starting data preprocessing...")
    
    try:
        from data_preprocessor import main as preprocess_main
        preprocess_main()
        logger.info("Data preprocessing completed successfully")
        return True
    except Exception as e:
        logger.error(f"Data preprocessing failed: {e}")
        return False

def run_vector_db_setup():
    """Run the vector database setup"""
    logger.info("Starting vector database setup...")
    
    try:
        from vector_db_setup import main as vector_main
        vector_main()
        logger.info("Vector database setup completed successfully")
        return True
    except Exception as e:
        logger.error(f"Vector database setup failed: {e}")
        return False

def test_rag_pipeline():
    """Test the RAG pipeline with a simple question"""
    logger.info("Testing RAG pipeline...")
    
    try:
        from rag_pipeline import BogleheadsRAGPipeline
        
        # Initialize the pipeline
        rag = BogleheadsRAGPipeline()
        
        # Test with a simple question
        test_question = "What are bonds?"
        logger.info(f"Testing with question: {test_question}")
        
        result = rag.ask_question(test_question, k=3)
        
        logger.info("Test completed successfully!")
        logger.info(f"Answer length: {len(result['answer'])} characters")
        logger.info(f"Sources found: {len(result['sources'])}")
        
        return True
        
    except Exception as e:
        logger.error(f"RAG pipeline test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("="*60)
    print("BOGLEHEADS RAG PIPELINE SETUP")
    print("="*60)
    
    # Step 1: Check requirements
    logger.info("Step 1: Checking requirements...")
    if not check_requirements():
        logger.error("Requirements check failed. Please fix the issues above.")
        return False
    
    # Step 2: Install dependencies
    logger.info("Step 2: Installing dependencies...")
    if not install_dependencies():
        logger.error("Dependency installation failed.")
        return False
    
    # Step 3: Data preprocessing
    logger.info("Step 3: Running data preprocessing...")
    if not run_data_preprocessing():
        logger.error("Data preprocessing failed.")
        return False
    
    # Step 4: Vector database setup
    logger.info("Step 4: Setting up vector database...")
    if not run_vector_db_setup():
        logger.error("Vector database setup failed.")
        return False
    
    # Step 5: Test the pipeline
    logger.info("Step 5: Testing the RAG pipeline...")
    if not test_rag_pipeline():
        logger.error("RAG pipeline test failed.")
        return False
    
    print("\n" + "="*60)
    print("SETUP COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("\nYou can now run the RAG pipeline with:")
    print("python rag_pipeline.py")
    print("\nOr start the interactive mode directly:")
    print("python -c \"from rag_pipeline import interactive_mode; interactive_mode()\"")
    print("\n" + "="*60)
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 