# Changelog

All notable changes to the Financial Knowledge RAG Pipeline project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-02

### 🎉 Initial Release

This is the first stable release of the Financial Knowledge RAG Pipeline, a privacy-first, locally-run system for financial advice and information retrieval.

### Added

#### Core Features
- **Hybrid RAG Pipeline**: Tiered approach using Q&A data first, then document fallback, then base LLM knowledge
- **Structured RAG Pipeline**: Context-aware Q&A system that eliminates confusion between similar topics
- **Privacy-First Architecture**: 100% local processing with no external API calls during queries
- **Verbosity Control**: Configurable output levels for production and debugging

#### Data Processing
- **Comprehensive Q&A Generator**: Extracts Q&A pairs from wiki content with 50+ categories
- **Data Quality Checker**: Validates factual accuracy and consistency
- **Q&A Content Manager**: Tools for curating and managing knowledge base
- **Vector Database Setup**: Efficient document storage and retrieval using ChromaDB

#### Scrapers & Processors
- **Bogleheads Wiki Scraper**: Automated scraping of financial knowledge from trusted sources
- **Data Preprocessor**: Converts HTML to structured text documents
- **Google Doc Processor**: Extracts Q&A pairs from Google Docs

#### Distribution
- **Pre-processed Q&A Data Package**: 26+ high-quality Q&A pairs covering key financial topics
- **Easy Installation**: Automated setup scripts for quick deployment
- **Sample Data**: Example datasets for testing and development

#### Documentation
- **Comprehensive README**: Complete project overview and quick start guide
- **Privacy Policy**: Detailed privacy guarantees and verification steps
- **Contributing Guide**: Workflow for financial experts to contribute via GitHub
- **Trusted Sources Guide**: List of government, professional, and educational sources
- **RAG Best Practices**: Implementation guidelines and design decisions
- **Quick Start Guide**: Step-by-step setup instructions
- **Google Doc Integration**: Guide for incorporating custom documents

#### Testing & Quality
- **Test Suite**: Comprehensive tests for pipelines and components
- **Privacy Verification**: Script to verify no external API calls
- **Data Quality Reports**: Automated validation and reporting

### Technical Details

#### Models & Embeddings
- **LLM**: Mistral-7b-Instruct-v0.1 (Q4_K_M quantization)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Vector Store**: ChromaDB with persistent storage

#### Categories Covered (50+)
- Traditional IRA, Roth IRA, 401(k), 403(b), 457 Plans
- HSA, FSA, ESA, 529 Plans
- Investment strategies, asset allocation, diversification
- Tax optimization, estate planning, retirement planning
- Social Security, Medicare, insurance
- And many more...

#### Privacy Features
- No external API calls during queries
- No data collection or transmission
- No model training on user data
- Complete offline capability after setup
- Open source for transparency

### Project Structure
- Organized codebase with clear separation of concerns
- `src/` for source code (core, generators, utils, pipelines)
- `scripts/` for standalone tools (scraping, setup, tools)
- `tests/` for test suite
- `docs/` for documentation
- `data/` for sample and Q&A data
- `distribution/` for pre-packaged data

### Dependencies
- Python 3.8+
- langchain, langchain-community, langchain-chroma
- llama-cpp-python
- sentence-transformers
- beautifulsoup4, requests
- chromadb, numpy

### Known Limitations
- Model file (4.1GB) must be downloaded separately
- CPU-only inference (GPU support can be enabled)
- English language only
- Focused on US financial system

### Future Roadmap
- Multi-source integration (IRS, SEC, SSA, etc.)
- Expert community building
- Multi-language support
- Advanced NLP techniques
- Performance optimizations

---

## Release Notes

### Installation
```bash
git clone <repository-url>
cd models
python scripts/setup/setup_repository.py
```

### Quick Start
```bash
# Quiet mode (default)
python src/core/hybrid_rag_pipeline.py

# Verbose mode for debugging
python src/core/hybrid_rag_pipeline.py --verbose
```

### Upgrade Notes
This is the initial release, so no upgrade path is needed.

### Contributors
- Abhinav Meduri - Initial development and architecture

### License
This project is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0).

---

For more information, see the [README](README.md) and [documentation](docs/).

