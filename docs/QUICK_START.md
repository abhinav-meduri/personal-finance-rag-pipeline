# Quick Start Guide

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
