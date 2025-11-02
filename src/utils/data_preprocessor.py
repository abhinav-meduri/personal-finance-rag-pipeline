#!/usr/bin/env python3
"""
Data Preprocessor for Bogleheads Wiki RAG Pipeline
Extracts text from HTML files and prepares them for vectorization
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import json
from tqdm import tqdm
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BogleheadsDataPreprocessor:
    def __init__(self, wiki_pages_dir: str = "wiki_pages", output_dir: str = "processed_data"):
        self.wiki_pages_dir = Path(wiki_pages_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Patterns to exclude
        self.exclude_patterns = [
            r'Special:',
            r'Category:',
            r'User:',
            r'File:',
            r'Bogleheads:',
            r'Talk:',
            r'Help:',
            r'Template:',
            r'Module:',
            r'MediaWiki:',
            r'robots\.txt',
            r'\.DS_Store'
        ]
        
    def is_binary_file(self, file_path: Path) -> bool:
        """Check if a file is binary"""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\x00' in chunk
        except Exception:
            return True
    
    def should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed"""
        # Skip directories
        if file_path.is_dir():
            return False
            
        # Skip binary files
        if self.is_binary_file(file_path):
            return False
            
        # Skip files matching exclude patterns
        file_str = str(file_path)
        for pattern in self.exclude_patterns:
            if re.search(pattern, file_str):
                return False
                
        return True
    
    def extract_text_from_html(self, html_content: str) -> str:
        """Extract clean text from HTML content"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Find the main content area (mw-content-text)
            content_div = soup.find('div', id='mw-content-text')
            if content_div:
                # Extract text from content div
                text = content_div.get_text(separator='\n', strip=True)
            else:
                # Fallback to body text
                text = soup.get_text(separator='\n', strip=True)
            
            # Clean up the text
            text = re.sub(r'\n\s*\n', '\n\n', text)  # Remove excessive newlines
            text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
            text = text.strip()
            
            return text
            
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            return ""
    
    def get_title_from_html(self, html_content: str, file_path: Path) -> str:
        """Extract title from HTML or use filename"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text().strip()
                # Clean up title
                title = re.sub(r' - Bogleheads$', '', title)
                return title
        except Exception:
            pass
        
        # Fallback to filename
        return file_path.stem.replace('_', ' ')
    
    def process_file(self, file_path: Path) -> Dict[str, Any]:
        """Process a single file and return metadata and content"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract text from HTML
            text = self.extract_text_from_html(content)
            
            if not text or len(text.strip()) < 100:  # Skip very short content
                return None
            
            # Extract title
            title = self.get_title_from_html(content, file_path)
            
            # Create metadata
            metadata = {
                'title': title,
                'source_file': str(file_path),
                'file_size': len(content),
                'text_length': len(text),
                'url': f"https://www.bogleheads.org/wiki/{file_path.stem}"
            }
            
            return {
                'content': text,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return None
    
    def process_all_files(self) -> List[Dict[str, Any]]:
        """Process all files in the wiki_pages directory"""
        processed_docs = []
        
        # Find all files recursively
        all_files = list(self.wiki_pages_dir.rglob('*'))
        logger.info(f"Found {len(all_files)} total files")
        
        # Filter files to process
        files_to_process = [f for f in all_files if self.should_process_file(f)]
        logger.info(f"Processing {len(files_to_process)} files")
        
        # Process each file
        for file_path in tqdm(files_to_process, desc="Processing files"):
            result = self.process_file(file_path)
            if result:
                processed_docs.append(result)
        
        logger.info(f"Successfully processed {len(processed_docs)} documents")
        return processed_docs
    
    def save_processed_data(self, processed_docs: List[Dict[str, Any]]):
        """Save processed data to JSON files"""
        # Save all documents
        all_docs_file = self.output_dir / "all_documents.json"
        with open(all_docs_file, 'w', encoding='utf-8') as f:
            json.dump(processed_docs, f, indent=2, ensure_ascii=False)
        
        # Save individual documents for easier processing
        docs_dir = self.output_dir / "documents"
        docs_dir.mkdir(exist_ok=True)
        
        for i, doc in enumerate(processed_docs):
            doc_file = docs_dir / f"doc_{i:05d}.json"
            with open(doc_file, 'w', encoding='utf-8') as f:
                json.dump(doc, f, indent=2, ensure_ascii=False)
        
        # Save metadata summary
        metadata_summary = {
            'total_documents': len(processed_docs),
            'total_text_length': sum(doc['metadata']['text_length'] for doc in processed_docs),
            'average_text_length': sum(doc['metadata']['text_length'] for doc in processed_docs) / len(processed_docs) if processed_docs else 0,
            'titles': [doc['metadata']['title'] for doc in processed_docs]
        }
        
        summary_file = self.output_dir / "metadata_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(metadata_summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved processed data to {self.output_dir}")
        logger.info(f"Total documents: {len(processed_docs)}")
        logger.info(f"Total text length: {metadata_summary['total_text_length']:,} characters")

def main():
    """Main function to run the data preprocessing"""
    preprocessor = BogleheadsDataPreprocessor()
    
    logger.info("Starting data preprocessing...")
    processed_docs = preprocessor.process_all_files()
    
    if processed_docs:
        preprocessor.save_processed_data(processed_docs)
        logger.info("Data preprocessing completed successfully!")
    else:
        logger.warning("No documents were processed successfully")

if __name__ == "__main__":
    main() 