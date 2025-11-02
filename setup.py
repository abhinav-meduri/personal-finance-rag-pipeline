#!/usr/bin/env python3
"""
Setup script for Financial Knowledge RAG Pipeline
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the version from VERSION file
version_file = Path(__file__).parent / "VERSION"
with open(version_file, "r") as f:
    version = f.read().strip()

# Read the long description from README
readme_file = Path(__file__).parent / "README.md"
with open(readme_file, "r", encoding="utf-8") as f:
    long_description = f.read()

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
with open(requirements_file, "r") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="personal-finance-rag-pipeline",
    version=version,
    author="Abhinav Meduri",
    author_email="",
    description="A privacy-first, local RAG system for financial advice and information",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/abhinav-meduri/personal-finance-rag-pipeline",
    packages=find_packages(include=["src", "src.*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: Creative Commons Attribution Share Alike 4.0 International",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "financial-rag=src.core.hybrid_rag_pipeline:main",
            "financial-rag-structured=src.core.structured_rag_pipeline:main",
            "financial-qa-manager=src.utils.qa_content_manager:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.md", "*.txt"],
    },
    zip_safe=False,
    keywords=[
        "rag",
        "retrieval-augmented-generation",
        "financial-advice",
        "llm",
        "mistral",
        "privacy",
        "local-ai",
        "bogleheads",
        "investing",
        "retirement-planning",
    ],
    project_urls={
        "Bug Reports": "https://github.com/abhinav-meduri/personal-finance-rag-pipeline/issues",
        "Source": "https://github.com/abhinav-meduri/personal-finance-rag-pipeline",
        "Documentation": "https://github.com/abhinav-meduri/personal-finance-rag-pipeline/tree/main/docs",
    },
)

