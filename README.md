# Financial Knowledge RAG Pipeline

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)

A Retrieval-Augmented Generation (RAG) pipeline that combines knowledge from trusted financial sources (such as Bogleheads Wiki) with Mistral-7b for intelligent financial advice and question answering.

## Privacy First: 100% Local Processing

**Your financial data and queries remain completely private and local to your computer.**

- **No External API Calls**: All processing happens locally
- **No Data Collection**: Your queries are never stored or transmitted
- **No Model Training**: Pre-trained models only, no learning from your data
- **Complete Offline Capability**: Works without internet after initial setup
- **Open Source**: Fully inspectable code for transparency

**[Complete Privacy Policy](PRIVACY.md) | [Privacy Verification Guide](PRIVACY.md#privacy-verification-steps)**

## Quick Start

### Automated Setup (Recommended)
```bash
git clone https://github.com/abhinav-meduri/personal-finance-rag-pipeline.git
cd personal-finance-rag-pipeline

# Install the package
pip install -e .

# Run setup script
python scripts/setup/setup_repository.py
```

### Manual Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download model and create sample data
python scripts/setup/setup_repository.py --model-only

# 3. Test with sample data
python src/core/structured_rag_pipeline.py --qa-data data/sample/sample_qa_data.json --question "What is a Roth IRA?"

# 4. Get comprehensive Q&A data (recommended)
# Download from: [LINK TO YOUR SHARED DATA]
# Or use the provided data package in the distribution/ folder
python distribution/install_qa_data.py

# 5. Scrape source data (optional - for expanding knowledge base)
python scripts/scraping/scrape_bogleheads_wiki.py
python src/utils/data_preprocessor.py
python src/generators/comprehensive_qa_generator.py
```

## What's Included

### Core Components
- **Structured RAG Pipeline**: Context-aware Q&A system that avoids confusion
- **Q&A Content Manager**: Tools for curating and managing knowledge base
- **Comprehensive Q&A Generator**: Extracts Q&A pairs from wiki content
- **Data Quality Checker**: Validates factual accuracy
- **Vector Database Setup**: Efficient document storage and retrieval

### Key Features
- **Complete Privacy**: 100% local processing, no external API calls
- **Context-Aware Answers**: Eliminates confusion between similar topics (e.g., Roth vs Traditional IRA)
- **Factual Accuracy**: Structured Q&A format reduces hallucinations
- **Easy Management**: Add, update, and validate Q&A pairs
- **Scalable**: Works with any knowledge base
- **Local Deployment**: Runs entirely on your machine

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Wiki Pages    │───▶│  Q&A Generator  │───▶│ Structured Q&A  │
│   (Scraped)     │    │                 │    │     Data        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Query    │◀───│  RAG Pipeline   │◀───│  Vector Store   │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘

ALL COMPONENTS RUN LOCALLY ON YOUR COMPUTER
   • No external API calls during queries
   • No data transmission to third parties
   • Complete privacy and security
```

## Repository Structure (v1.0.0)

```
models/
├── src/                               # Source Code
│   ├── core/                          # Core RAG pipelines
│   │   ├── hybrid_rag_pipeline.py    # Tiered hybrid approach
│   │   ├── structured_rag_pipeline.py # Context-aware Q&A
│   │   └── rag_pipeline.py           # Basic RAG pipeline
│   │
│   ├── generators/                    # Q&A data generators
│   │   ├── comprehensive_qa_generator.py
│   │   ├── structured_qa_generator.py
│   │   └── google_doc_processor.py
│   │
│   ├── utils/                         # Utility modules
│   │   ├── data_preprocessor.py      # HTML to text
│   │   ├── vector_db_setup.py        # Vector database
│   │   ├── qa_content_manager.py     # Q&A management
│   │   └── data_quality_checker.py   # Quality validation
│   │
│   └── pipelines/                     # Pipeline configurations
│       └── setup_hybrid_rag.py
│
├── scripts/                           # Standalone Scripts
│   ├── scraping/                      # Web scrapers
│   │   ├── scrape_bogleheads_wiki.py
│   │   └── scrape_bogleheads.py
│   │
│   ├── setup/                         # Setup scripts
│   │   ├── setup_repository.py       # Complete setup
│   │   └── setup_rag_pipeline.py
│   │
│   └── tools/                         # Utility tools
│       ├── data_distribution.py
│       ├── privacy_verification.py
│       └── binary_files_checker.sh
│
├── tests/                             # Test Suite
│   ├── test_pipeline.py
│   ├── test_rag_comparison.py
│   └── test_verbosity.py
│
├── docs/                              # Documentation
│   ├── CONTRIBUTING.md
│   ├── PRIVACY.md
│   ├── QUICK_START.md
│   ├── PROJECT_VISION.md
│   ├── RAG_BEST_PRACTICES.md
│   ├── TRUSTED_SOURCES_GUIDE.md
│   ├── DATA_SHARING_GUIDE.md
│   ├── GOOGLE_DOC_INTEGRATION.md
│   └── REPOSITORY_SUMMARY.md
│
├── data/                              # Data Files
│   ├── sample/
│   │   └── sample_qa_data.json       # Sample data for testing
│   │
│   └── qa/
│       ├── comprehensive_qa_data.json # Full Q&A knowledge base
│       └── structured_qa_data.json   # Focused Q&A pairs
│
├── distribution/                      # Distribution Packages
│   ├── bogleheads_qa_data.json
│   ├── comprehensive_qa_data.json
│   ├── install_qa_data.py
│   ├── README.md
│   ├── categories.md
│   └── sample_questions.md
│
├── examples/                          # Example Files
│   └── financial_advice_20yo.txt
│
├── Project Files
│   ├── README.md                      # This file
│   ├── LICENSE                        # CC BY-SA 4.0
│   ├── VERSION                        # 1.0.0
│   ├── CHANGELOG.md                   # Change history
│   ├── requirements.txt               # Dependencies
│   ├── setup.py                       # Package setup
│   ├── MANIFEST.in                    # Package manifest
│   ├── QUICK_REFERENCE.md             # Quick command reference
│   └── RELEASE_CHECKLIST.md           # Release preparation
│
└── Generated Directories (not in Git)
    ├── vector_db/                     # Vector database (267MB)
    ├── structured_vector_db/          # Structured vectors (16MB)
    ├── qa_vector_db/                  # Q&A vectors
    ├── processed_data/                # Processed documents (18MB)
    ├── wiki_pages/                    # Scraped pages (76MB)
    └── qa_backups/                    # Q&A backups
```

## Usage Examples

### Interactive Mode
```bash
# Quiet mode (default) - minimal output
python src/core/hybrid_rag_pipeline.py

# Verbose mode - detailed debug information
python src/core/hybrid_rag_pipeline.py --verbose
# or
python src/core/hybrid_rag_pipeline.py -v

# Using installed package (after pip install -e .)
financial-rag
financial-rag --verbose
```

### Single Question
```bash
python src/core/structured_rag_pipeline.py --question "Do Roth IRAs have required minimum distributions?"

# Or using installed package
financial-rag-structured --question "Do Roth IRAs have required minimum distributions?"
```

### Verbosity Control

The hybrid RAG pipeline supports different verbosity levels:

- **Quiet Mode (default)**: Minimal output, clean interface
- **Verbose Mode**: Detailed debug information, logging, and processing steps

**When to use verbose mode:**
- Debugging issues
- Understanding how the pipeline processes queries
- Development and testing
- Troubleshooting vector database or model issues

**When to use quiet mode:**
- Normal usage
- Production environments
- Clean user experience
- Batch processing

### Manage Q&A Content
```bash
# Add new Q&A pair
python src/utils/qa_content_manager.py --add

# Search Q&A pairs
python src/utils/qa_content_manager.py --search "Roth IRA"

# Validate data quality
python src/utils/qa_content_manager.py --validate

# Export specific category
python src/utils/qa_content_manager.py --export traditional_ira_basics

# Or using installed package
financial-qa-manager --add
financial-qa-manager --search "Roth IRA"
```

## Q&A Data Package

### Quick Start with Pre-Processed Data

Instead of scraping source pages, you can use our pre-processed Q&A data package:

**Option 1: Use Included Package**
```bash
# The distribution/ folder contains a ready-to-use Q&A package
python distribution/install_qa_data.py
```

**Option 2: Download from Release**
```bash
# Download the latest Q&A data package from releases
# [LINK TO YOUR RELEASE]
```

### What's Included in the Q&A Package

- **26 High-Quality Q&A Pairs** covering key financial topics
- **20 Categories** including IRAs, 401(k)s, investments, taxes, etc.
- **Context-Aware Answers** that avoid confusion between similar topics
- **High Confidence Scores** indicating reliable information
- **Proper Attribution** to trusted financial sources
- **Easy Integration** with the RAG pipeline

### Categories Covered

- **Traditional IRA**: basics, contributions, withdrawals, tax implications
- **Roth IRA**: basics, contributions, withdrawals, tax implications  
- **401(k) Plans**: basics, contributions, withdrawals
- **Investment Strategies**: index funds, asset allocation, diversification
- **Tax Optimization**: qualified dividends, tax planning strategies
- **Retirement Planning**: Social Security, RMD rules, estate planning
- **Account Comparisons**: IRA vs 401(k), Traditional vs Roth analysis

### Benefits of Using the Q&A Package

1. **Instant Setup**: No need to scrape wiki pages
2. **Proven Quality**: Pre-validated Q&A pairs with high confidence
3. **Focused Answers**: Context-aware responses that avoid confusion
4. **Better Performance**: Faster queries and more accurate results
5. **Easy Updates**: Simple to add new Q&A pairs as needed

## Configuration

### Model Settings
- **LLM**: Mistral-7b-instruct (4-bit quantized)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Vector Database**: ChromaDB
- **Chunk Size**: 1000 characters with 200 character overlap

### Performance
- **Memory Usage**: ~4GB RAM (model) + ~1GB (embeddings)
- **Query Speed**: 2-5 seconds per question
- **Vector Search**: <1 second

## Contributing

### Adding New Q&A Pairs
1. Use the content manager: `python src/utils/qa_content_manager.py --add`
2. Or edit `data/qa/comprehensive_qa_data.json` directly
3. Validate your changes: `python src/utils/qa_content_manager.py --validate`

### Improving the Knowledge Base
1. **Scrape new content**: `python scripts/scraping/scrape_bogleheads_wiki.py`
2. **Generate Q&A pairs**: `python src/generators/comprehensive_qa_generator.py`
3. **Quality check**: `python src/utils/data_quality_checker.py`
4. **Test changes**: `python tests/test_pipeline.py`
5. **Expert curation**: Use the content manager for domain expert contributions

### Code Contributions
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Performance Benefits

### Structured Q&A vs Document RAG
| Aspect | Document RAG | Structured Q&A |
|--------|-------------|----------------|
| **Speed** | Slower (full doc search) | Faster (direct Q&A matching) |
| **Accuracy** | Context confusion | Clear, focused answers |
| **Memory** | Large vector space | Compact Q&A embeddings |
| **Maintenance** | Complex document management | Simple Q&A curation |
| **Scalability** | Limited by document size | Scales with Q&A pairs |

## Testing

### Run All Tests
```bash
python tests/test_pipeline.py
python tests/test_rag_comparison.py
python tests/test_verbosity.py
```

### Test Specific Components
```bash
# Test structured RAG
python src/core/structured_rag_pipeline.py --question "What is a Roth IRA?"

# Test Q&A management
python src/utils/qa_content_manager.py --validate

# Test data quality
python src/utils/data_quality_checker.py
```

## Troubleshooting

### Common Issues

1. **Model Download Fails**
   ```bash
   # Manual download
   wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf
   ```

2. **Out of Memory**
   - Reduce model parameters in `structured_rag_pipeline.py`
   - Use CPU mode instead of GPU

3. **Dependencies Installation Failed**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

4. **Vector Database Issues**
   ```bash
   # Recreate vector database
   python src/utils/vector_db_setup.py --recreate
   ```

5. **Privacy Verification**
   ```bash
   # Verify no network activity during queries
   sudo tcpdump -i any -w query_monitor.pcap
   python src/core/hybrid_rag_pipeline.py --question "What is a Roth IRA?"
   # Check: no network packets during query processing
   ```

## Roadmap

### Phase 1: Foundation (Current)
- [x] Structured Q&A approach for accuracy
- [x] Bogleheads Wiki integration
- [x] Expert curation workflow
- [x] Data sharing and distribution

### Phase 2: Source Expansion (Next 3 months)
- [ ] Add IRS as trusted source for tax information
- [ ] Integrate SEC for investment regulations
- [ ] Include Social Security Administration for retirement benefits
- [ ] Implement multi-source content merging

### Phase 3: Expert Community (3-6 months)
- [ ] Establish expert review and validation process
- [ ] Create professional contribution workflow
- [ ] Implement source attribution and quality scoring
- [ ] Build expert recognition and attribution system

### Phase 4: Advanced Features (6+ months)
- [ ] Implement hybrid RAG (document + structured Q&A)
- [ ] Add real-time regulatory updates
- [ ] Create web interface for expert contributions
- [ ] Add multi-language support
- [ ] Implement automated quality validation pipeline

### Long-term Vision
- [ ] Become the most comprehensive financial knowledge base
- [ ] Establish industry standard for financial AI accuracy
- [ ] Create global expert community for financial education
- [ ] Enable real-time regulatory compliance updates

## License

This project is licensed under **Creative Commons Attribution-ShareAlike 4.0 International License** (CC BY-SA 4.0).

### What This Means

**You are free to:**
- **Share** - Copy and redistribute the material in any medium or format
- **Adapt** - Remix, transform, and build upon the material for any purpose, even commercially
- **Use** - Use the material for any purpose, including commercial applications

**Under the following terms:**
- **Attribution** - You must give appropriate credit to the original authors
- **ShareAlike** - If you remix, transform, or build upon the material, you must distribute your contributions under the same license

### Attribution Requirements

When using this project, please include:

1. **Original Authors**: Credit to the contributors of this Bogleheads RAG Pipeline
2. **Bogleheads Wiki**: Credit to the Bogleheads community for the comprehensive financial information
3. **License Link**: Link to the full license: https://creativecommons.org/licenses/by-sa/4.0/

### Example Attribution

```
Bogleheads RAG Pipeline by [Your Name]
Based on comprehensive financial information from the Bogleheads Wiki community
Licensed under CC BY-SA 4.0: https://creativecommons.org/licenses/by-sa/4.0/
```

### Bogleheads Wiki License

The source content from the [Bogleheads Wiki](https://www.bogleheads.org/wiki/Main_Page) is also licensed under Creative Commons Attribution-ShareAlike 4.0 International License, which allows us to use and adapt their comprehensive financial information while maintaining proper attribution.

## Acknowledgments

### Primary Knowledge Sources
**[Bogleheads Wiki](https://www.bogleheads.org/wiki/Main_Page)** - The comprehensive financial knowledge base that makes this project possible. The Bogleheads community has created an invaluable resource covering investment strategies, retirement planning, tax considerations, and much more.

**Financial Experts** - Domain professionals who contribute their expertise through curated Q&A pairs, ensuring accuracy, relevance, and practical value for users.

**Trusted Financial Sources** - Various authoritative sources that provide the foundation for our knowledge base, including regulatory bodies, professional organizations, and educational institutions.

### Technical Infrastructure
- [Mistral AI](https://mistral.ai/) for the powerful Mistral-7b language model
- [LangChain](https://langchain.com/) for the RAG framework and tools
- [ChromaDB](https://www.trychroma.com/) for efficient vector storage
- [Hugging Face](https://huggingface.co/) for model hosting and embeddings

### Privacy & Security
- **Local Processing**: All components designed for local execution
- **No External Dependencies**: Self-contained system for maximum privacy
- **Open Source**: Fully inspectable code for transparency
- **Community Verification**: Privacy claims verified by the community

### Community
- The Bogleheads community for maintaining and expanding the wiki
- Contributors to the Bogleheads investing philosophy
- The open-source AI/ML community for making these tools accessible

## Support

- **Issues**: Create a GitHub issue
- **Questions**: Check the [QUICK_START.md](QUICK_START.md) guide
- **Contributions**: Submit a pull request
- **Privacy Concerns**: Review [PRIVACY.md](PRIVACY.md) or create a GitHub issue

---

**Note**: This is a research project. Always verify financial advice with qualified professionals.

---

**License**: This project is licensed under Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0). See the [License section](#license) above for details. 