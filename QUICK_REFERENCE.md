# Quick Reference Guide - v1.0.0

Quick reference for common tasks in the reorganized structure.

##  Running the Pipeline

### Hybrid RAG Pipeline (Recommended)
```bash
# Quiet mode (default)
python src/core/hybrid_rag_pipeline.py

# Verbose mode (for debugging)
python src/core/hybrid_rag_pipeline.py --verbose

# After installation
financial-rag
financial-rag --verbose
```

### Structured RAG Pipeline
```bash
python src/core/structured_rag_pipeline.py

# With specific Q&A data
python src/core/structured_rag_pipeline.py --qa-data data/qa/comprehensive_qa_data.json

# After installation
financial-rag-structured
```

##  Managing Q&A Data

### Add New Q&A Pair
```bash
python src/utils/qa_content_manager.py --add
# Or: financial-qa-manager --add
```

### Search Q&A Pairs
```bash
python src/utils/qa_content_manager.py --search "Roth IRA"
# Or: financial-qa-manager --search "Roth IRA"
```

### Validate Data Quality
```bash
python src/utils/qa_content_manager.py --validate
```

### Export Category
```bash
python src/utils/qa_content_manager.py --export traditional_ira_basics
```

##  Setup and Installation

### First Time Setup
```bash
# Install package
pip install -e .

# Run setup script
python scripts/setup/setup_repository.py
```

### Install with Dev Dependencies
```bash
pip install -e ".[dev]"
```

##  Testing

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run Specific Test
```bash
python tests/test_pipeline.py
python tests/test_verbosity.py
```

### Verify Privacy
```bash
python scripts/tools/privacy_verification.py
```

## 🌐 Scraping and Data Processing

### Scrape Bogleheads Wiki
```bash
python scripts/scraping/scrape_bogleheads_wiki.py
```

### Process Scraped Data
```bash
python src/utils/data_preprocessor.py
```

### Generate Q&A Data
```bash
python src/generators/comprehensive_qa_generator.py
```

### Process Google Doc
```bash
python src/generators/google_doc_processor.py --input examples/financial_advice_20yo.txt
```

## Vector Database

### Setup Vector Database
```bash
python src/utils/vector_db_setup.py
```

### Setup Hybrid RAG
```bash
python src/pipelines/setup_hybrid_rag.py
```

##  Distribution

### Create Distribution Package
```bash
python scripts/tools/data_distribution.py
```

### Install Q&A Data Package
```bash
python distribution/install_qa_data.py
```

## 📁 File Locations

### Core Pipelines
- `src/core/hybrid_rag_pipeline.py` - Hybrid approach
- `src/core/structured_rag_pipeline.py` - Structured Q&A
- `src/core/rag_pipeline.py` - Basic pipeline

### Q&A Generators
- `src/generators/comprehensive_qa_generator.py` - Main generator
- `src/generators/structured_qa_generator.py` - Structured generator
- `src/generators/google_doc_processor.py` - Google Doc processor

### Utilities
- `src/utils/data_preprocessor.py` - Data preprocessing
- `src/utils/vector_db_setup.py` - Vector database
- `src/utils/qa_content_manager.py` - Q&A management
- `src/utils/data_quality_checker.py` - Quality checking

### Scripts
- `scripts/scraping/scrape_bogleheads_wiki.py` - Wiki scraper
- `scripts/setup/setup_repository.py` - Complete setup
- `scripts/tools/privacy_verification.py` - Privacy verification

### Data
- `data/sample/sample_qa_data.json` - Sample data
- `data/qa/comprehensive_qa_data.json` - Full Q&A data
- `data/qa/structured_qa_data.json` - Structured Q&A

### Documentation
- `docs/CONTRIBUTING.md` - How to contribute
- `docs/PRIVACY.md` - Privacy policy
- `docs/QUICK_START.md` - Getting started
- `docs/RAG_BEST_PRACTICES.md` - Best practices

##  Common Issues

### Import Errors
If you get import errors, install the package:
```bash
pip install -e .
```

### Model Not Found
Download the model file separately (4.1GB):
```bash
# See README.md for download link
```

### Vector Database Missing
Regenerate vector databases:
```bash
python src/utils/vector_db_setup.py
python src/pipelines/setup_hybrid_rag.py
```

### Permission Errors
Make scripts executable:
```bash
chmod +x scripts/tools/binary_files_checker.sh
```

##  Documentation

### Main Documentation
- `README.md` - Project overview
- `CHANGELOG.md` - Version history
- `MIGRATION_GUIDE.md` - Migration from old structure
- `PROJECT_STRUCTURE.md` - Structure details
- `RELEASE_CHECKLIST.md` - Release preparation

### Guides
- `docs/QUICK_START.md` - Getting started
- `docs/CONTRIBUTING.md` - Contributing guide
- `docs/PRIVACY.md` - Privacy policy
- `docs/GOOGLE_DOC_INTEGRATION.md` - Google Doc integration
- `docs/TRUSTED_SOURCES_GUIDE.md` - Trusted sources

##  Quick Commands Cheatsheet

```bash
# Run pipeline
financial-rag

# Run with debug output
financial-rag --verbose

# Add Q&A pair
financial-qa-manager --add

# Search Q&A
financial-qa-manager --search "keyword"

# Run tests
pytest tests/

# Verify privacy
python scripts/tools/privacy_verification.py

# Setup everything
python scripts/setup/setup_repository.py

# Generate Q&A
python src/generators/comprehensive_qa_generator.py

# Process data
python src/utils/data_preprocessor.py

# Setup vector DB
python src/utils/vector_db_setup.py
```

## 🆘 Getting Help

1. Check `README.md` for overview
2. Read `docs/QUICK_START.md` for setup
3. See `MIGRATION_GUIDE.md` for structure changes
4. Review `docs/` for specific guides
5. Open an issue on GitHub

##  Notes

- All commands assume you're in the project root directory
- Use `--verbose` flag for debugging
- Model file (4.1GB) must be downloaded separately
- Vector databases can be regenerated from data
- Old files remain in root for backward compatibility

---

**Version**: 1.0.0  
**Last Updated**: November 2, 2025

