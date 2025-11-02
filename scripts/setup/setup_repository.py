#!/usr/bin/env python3
"""
Repository Setup Script
Complete setup script for new users to replicate the Bogleheads RAG pipeline.
"""

import os
import sys
import subprocess
import json
import requests
from pathlib import Path
import argparse
from tqdm import tqdm

class RepositorySetup:
    def __init__(self):
        self.model_url = "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
        self.model_filename = "mistral-7b-instruct-v0.1.Q4_K_M.gguf"
        self.required_dirs = [
            "data",
            "wiki_pages", 
            "processed_data",
            "vector_db",
            "structured_vector_db",
            "qa_backups"
        ]
        
    def check_python_version(self):
        """Check if Python version is compatible."""
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ is required")
            sys.exit(1)
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    def install_dependencies(self):
        """Install required Python packages."""
        print("📦 Installing dependencies...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                         check=True, capture_output=True)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            sys.exit(1)
    
    def create_directories(self):
        """Create required directories."""
        print("📁 Creating directories...")
        for dir_name in self.required_dirs:
            Path(dir_name).mkdir(exist_ok=True)
        print("✅ Directories created")
    
    def download_model(self, force=False):
        """Download the Mistral-7b model."""
        if os.path.exists(self.model_filename) and not force:
            print(f"✅ Model already exists: {self.model_filename}")
            return
        
        print(f"📥 Downloading model: {self.model_filename}")
        print("⚠️  This is a large file (~4GB) and may take a while...")
        
        try:
            response = requests.get(self.model_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(self.model_filename, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading") as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            
            print("✅ Model downloaded successfully")
        except Exception as e:
            print(f"❌ Failed to download model: {e}")
            print("💡 You can manually download the model from:")
            print(f"   {self.model_url}")
            sys.exit(1)
    
    def scrape_wiki_data(self):
        """Scrape Bogleheads wiki data."""
        print("🌐 Scraping Bogleheads wiki data...")
        try:
            # Run the wiki scraper
            subprocess.run([sys.executable, "scrape_bogleheads_wiki.py"], check=True)
            print("✅ Wiki data scraped successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to scrape wiki data: {e}")
            print("💡 You can run this manually later with: python scrape_bogleheads_wiki.py")
    
    def process_data(self):
        """Process the scraped data."""
        print("🔧 Processing wiki data...")
        try:
            subprocess.run([sys.executable, "data_preprocessor.py"], check=True)
            print("✅ Data processed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to process data: {e}")
            print("💡 You can run this manually later with: python data_preprocessor.py")
    
    def generate_qa_data(self):
        """Generate structured Q&A data."""
        print("📝 Generating structured Q&A data...")
        try:
            subprocess.run([sys.executable, "comprehensive_qa_generator.py"], check=True)
            print("✅ Q&A data generated successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to generate Q&A data: {e}")
            print("💡 You can run this manually later with: python comprehensive_qa_generator.py")
    
    def setup_vector_db(self):
        """Set up vector database."""
        print("🗄️  Setting up vector database...")
        try:
            subprocess.run([sys.executable, "vector_db_setup.py"], check=True)
            print("✅ Vector database set up successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to set up vector database: {e}")
            print("💡 You can run this manually later with: python vector_db_setup.py")
    
    def test_pipeline(self):
        """Test the RAG pipeline."""
        print("🧪 Testing RAG pipeline...")
        try:
            result = subprocess.run([sys.executable, "test_pipeline.py"], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print("✅ Pipeline test passed")
            else:
                print("⚠️  Pipeline test failed, but setup is complete")
                print("💡 You can test manually with: python test_pipeline.py")
        except subprocess.TimeoutExpired:
            print("⚠️  Pipeline test timed out, but setup is complete")
        except Exception as e:
            print(f"⚠️  Pipeline test failed: {e}")
    
    def create_sample_data(self):
        """Create sample Q&A data for immediate testing."""
        print("📋 Creating sample Q&A data...")
        
        sample_qa = {
            "metadata": {
                "total_qa_pairs": 5,
                "categories": ["sample"],
                "category_counts": {"sample": 5},
                "sources": ["sample"],
                "last_updated": "2025-01-01T00:00:00"
            },
            "qa_pairs": [
                {
                    "question": "What is a Roth IRA?",
                    "answer": "A Roth IRA is an individual retirement account with after-tax contributions and tax-free growth and withdrawals for qualified distributions.",
                    "context": "Roth IRA definition",
                    "source": "sample",
                    "doc_id": "sample_001",
                    "category": "sample",
                    "confidence": "high"
                },
                {
                    "question": "Do Roth IRAs have required minimum distributions?",
                    "answer": "No, Roth IRAs have no required minimum distributions during the owner's lifetime.",
                    "context": "Roth IRA RMD rules",
                    "source": "sample",
                    "doc_id": "sample_002",
                    "category": "sample",
                    "confidence": "high"
                },
                {
                    "question": "What are the 2024 Roth IRA contribution limits?",
                    "answer": "For 2024, the Roth IRA contribution limit is $7,000 ($8,000 for those age 50 or older).",
                    "context": "Roth IRA contribution rules",
                    "source": "sample",
                    "doc_id": "sample_003",
                    "category": "sample",
                    "confidence": "high"
                },
                {
                    "question": "What is a 401(k) plan?",
                    "answer": "A 401(k) is an employer-sponsored retirement plan that allows employees to contribute pre-tax dollars with potential employer matching.",
                    "context": "401(k) definition",
                    "source": "sample",
                    "doc_id": "sample_004",
                    "category": "sample",
                    "confidence": "high"
                },
                {
                    "question": "What is an index fund?",
                    "answer": "An index fund is a mutual fund or ETF that tracks a specific market index, providing broad market exposure at low cost.",
                    "context": "Index fund definition",
                    "source": "sample",
                    "doc_id": "sample_005",
                    "category": "sample",
                    "confidence": "high"
                }
            ]
        }
        
        with open("sample_qa_data.json", "w") as f:
            json.dump(sample_qa, f, indent=2)
        
        print("✅ Sample Q&A data created")
    
    def create_quick_start_guide(self):
        """Create a quick start guide."""
        guide = """# Quick Start Guide

## Prerequisites
- Python 3.8+
- 8GB+ RAM
- 10GB+ disk space

## Quick Setup (Automated)
```bash
python setup_repository.py
```

## Manual Setup Steps
1. Install dependencies: `pip install -r requirements.txt`
2. Download model: `python setup_repository.py --model-only`
3. Scrape wiki data: `python scrape_bogleheads_wiki.py`
4. Process data: `python data_preprocessor.py`
5. Generate Q&A: `python comprehensive_qa_generator.py`
6. Setup vector DB: `python vector_db_setup.py`

## Usage
- Interactive mode: `python structured_rag_pipeline.py`
- Single question: `python structured_rag_pipeline.py --question "What is a Roth IRA?"`
- Manage Q&A data: `python qa_content_manager.py --help`

## Sample Data
For immediate testing, use the sample data:
```bash
python structured_rag_pipeline.py --qa-data sample_qa_data.json --question "What is a Roth IRA?"
```

## Contributing
- Add new Q&A pairs: `python qa_content_manager.py --add`
- Validate data: `python qa_content_manager.py --validate`
- Export categories: `python qa_content_manager.py --export traditional_ira_basics`
"""
        
        with open("QUICK_START.md", "w") as f:
            f.write(guide)
        
        print("✅ Quick start guide created")
    
    def run_setup(self, skip_model=False, skip_wiki=False, force_model=False):
        """Run the complete setup process."""
        print("🚀 Starting Bogleheads RAG Pipeline Setup")
        print("=" * 50)
        
        # Check Python version
        self.check_python_version()
        
        # Create directories
        self.create_directories()
        
        # Install dependencies
        self.install_dependencies()
        
        # Download model (unless skipped)
        if not skip_model:
            self.download_model(force=force_model)
        
        # Create sample data for immediate testing
        self.create_sample_data()
        
        # Scrape wiki data (unless skipped)
        if not skip_wiki:
            self.scrape_wiki_data()
            self.process_data()
            self.generate_qa_data()
            self.setup_vector_db()
        
        # Create quick start guide
        self.create_quick_start_guide()
        
        # Test pipeline
        self.test_pipeline()
        
        print("\n" + "=" * 50)
        print("✅ Setup Complete!")
        print("\n📚 Next Steps:")
        print("1. Test with sample data: python structured_rag_pipeline.py --qa-data sample_qa_data.json")
        print("2. Scrape wiki data: python scrape_bogleheads_wiki.py")
        print("3. Generate full Q&A: python comprehensive_qa_generator.py")
        print("4. Start interactive mode: python structured_rag_pipeline.py")
        print("\n📖 See QUICK_START.md for detailed instructions")

def main():
    parser = argparse.ArgumentParser(description='Setup Bogleheads RAG Pipeline')
    parser.add_argument('--skip-model', action='store_true', 
                       help='Skip model download (use existing model)')
    parser.add_argument('--skip-wiki', action='store_true',
                       help='Skip wiki scraping and processing')
    parser.add_argument('--force-model', action='store_true',
                       help='Force re-download of model')
    parser.add_argument('--model-only', action='store_true',
                       help='Only download model and create sample data')
    
    args = parser.parse_args()
    
    setup = RepositorySetup()
    
    if args.model_only:
        setup.check_python_version()
        setup.create_directories()
        setup.install_dependencies()
        setup.download_model(force=args.force_model)
        setup.create_sample_data()
        setup.create_quick_start_guide()
        print("✅ Model setup complete!")
    else:
        setup.run_setup(
            skip_model=args.skip_model,
            skip_wiki=args.skip_wiki,
            force_model=args.force_model
        )

if __name__ == "__main__":
    main() 