#!/usr/bin/env python3
"""
Vector Database Setup for Bogleheads Wiki RAG Pipeline
Creates embeddings and stores them in ChromaDB
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
import logging
from tqdm import tqdm

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BogleheadsVectorDB:
    def __init__(self, 
                 processed_data_dir: str = "processed_data",
                 vector_db_dir: str = "vector_db",
                 model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.processed_data_dir = Path(processed_data_dir)
        self.vector_db_dir = Path(vector_db_dir)
        self.model_name = model_name
        
        # Create directories
        self.vector_db_dir.mkdir(exist_ok=True)
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Initialize embeddings model
        logger.info(f"Loading embeddings model: {model_name}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},  # Use CPU for compatibility
            encode_kwargs={'normalize_embeddings': True}
        )
        
    def load_processed_documents(self) -> List[Dict[str, Any]]:
        """Load processed documents from JSON files"""
        all_docs_file = self.processed_data_dir / "all_documents.json"
        
        if not all_docs_file.exists():
            raise FileNotFoundError(f"Processed documents file not found: {all_docs_file}")
        
        with open(all_docs_file, 'r', encoding='utf-8') as f:
            documents = json.load(f)
        
        logger.info(f"Loaded {len(documents)} processed documents")
        return documents
    
    def create_documents(self, processed_docs: List[Dict[str, Any]]) -> List[Document]:
        """Convert processed documents to LangChain Document objects"""
        documents = []
        
        for doc in tqdm(processed_docs, desc="Creating documents"):
            content = doc['content']
            metadata = doc['metadata']
            
            # Split text into chunks
            chunks = self.text_splitter.split_text(content)
            
            # Create Document objects for each chunk
            for i, chunk in enumerate(chunks):
                chunk_metadata = metadata.copy()
                chunk_metadata['chunk_id'] = i
                chunk_metadata['total_chunks'] = len(chunks)
                
                document = Document(
                    page_content=chunk,
                    metadata=chunk_metadata
                )
                documents.append(document)
        
        logger.info(f"Created {len(documents)} document chunks")
        return documents
    
    def create_vector_store(self, documents: List[Document]) -> Chroma:
        """Create and populate the vector store"""
        logger.info("Creating vector store...")
        
        # Create ChromaDB vector store
        vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=str(self.vector_db_dir)
        )
        
        # Vector store is automatically persisted in Chroma 0.4.x+
        
        logger.info(f"Vector store created and saved to {self.vector_db_dir}")
        return vector_store
    
    def get_vector_store(self) -> Chroma:
        """Load existing vector store"""
        if not self.vector_db_dir.exists():
            raise FileNotFoundError(f"Vector database directory not found: {self.vector_db_dir}")
        
        vector_store = Chroma(
            persist_directory=str(self.vector_db_dir),
            embedding_function=self.embeddings
        )
        
        return vector_store
    
    def search_similar(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        vector_store = self.get_vector_store()
        
        results = vector_store.similarity_search_with_score(query, k=k)
        
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                'content': doc.page_content,
                'metadata': doc.metadata,
                'similarity_score': float(score)
            })
        
        return formatted_results
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        vector_store = self.get_vector_store()
        collection = vector_store._collection
        
        stats = {
            'total_documents': collection.count(),
            'embedding_dimension': 384,  # all-MiniLM-L6-v2 dimension
            'collection_name': collection.name
        }
        
        return stats

def main():
    """Main function to set up the vector database"""
    try:
        # Initialize vector database
        vector_db = BogleheadsVectorDB()
        
        # Load processed documents
        logger.info("Loading processed documents...")
        processed_docs = vector_db.load_processed_documents()
        
        # Create document chunks
        logger.info("Creating document chunks...")
        documents = vector_db.create_documents(processed_docs)
        
        # Create vector store
        logger.info("Creating vector store...")
        vector_store = vector_db.create_vector_store(documents)
        
        # Get statistics
        stats = vector_db.get_collection_stats()
        logger.info(f"Vector database statistics: {stats}")
        
        # Test search
        logger.info("Testing search functionality...")
        test_query = "What are the basics of bond investing?"
        results = vector_db.search_similar(test_query, k=3)
        
        logger.info(f"Test query: '{test_query}'")
        for i, result in enumerate(results):
            logger.info(f"Result {i+1}: {result['metadata']['title']} (score: {result['similarity_score']:.4f})")
        
        logger.info("Vector database setup completed successfully!")
        
    except Exception as e:
        logger.error(f"Error setting up vector database: {e}")
        raise

if __name__ == "__main__":
    main() 