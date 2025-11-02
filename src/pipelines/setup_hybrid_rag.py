#!/usr/bin/env python3
"""
Hybrid RAG Pipeline Setup - Best Practice Deployment
Allows users to choose their preferred complexity level while maintaining optimal performance.
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, Any, List
import argparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HybridRAGSetup:
    """
    Setup class implementing best practices for RAG pipeline deployment
    """
    
    def __init__(self):
        self.base_dir = Path.cwd()
        self.qa_data_path = self.base_dir / "comprehensive_qa_data.json"
        self.sample_qa_path = self.base_dir / "sample_qa_data.json"
        
    def create_qa_vector_db(self, qa_data_path: str, output_dir: str = "qa_vector_db"):
        """Create vector database from Q&A data"""
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            from langchain_chroma import Chroma
            from langchain.schema import Document
            
            # Load Q&A data
            with open(qa_data_path, 'r', encoding='utf-8') as f:
                qa_data = json.load(f)
            
            # Create documents from Q&A pairs
            documents = []
            for qa_pair in qa_data['qa_pairs']:
                content = f"Context: {qa_pair['context']}\n\nQuestion: {qa_pair['question']}\n\nAnswer: {qa_pair['answer']}"
                
                metadata = {
                    'source': qa_pair['source'],
                    'category': qa_pair['category'],
                    'context': qa_pair['context'],
                    'question': qa_pair['question'],
                    'doc_id': qa_pair['doc_id']
                }
                
                doc = Document(page_content=content, metadata=metadata)
                documents.append(doc)
            
            # Create embeddings
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
            
            # Create vector store
            vector_store = Chroma.from_documents(
                documents=documents,
                embedding=embeddings,
                persist_directory=output_dir
            )
            vector_store.persist()
            
            logger.info(f"Created QA vector database with {len(documents)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Error creating QA vector database: {e}")
            return False
    
    def setup_minimal_deployment(self) -> bool:
        """
        Minimal deployment: QA data only
        - Fastest setup
        - Smallest footprint
        - High accuracy for covered topics
        """
        logger.info("Setting up minimal deployment (QA data only)...")
        
        # Check if QA data exists
        if not self.qa_data_path.exists():
            logger.error("QA data file not found. Please run comprehensive_qa_generator.py first.")
            return False
        
        # Create QA vector database
        if not self.create_qa_vector_db(str(self.qa_data_path)):
            return False
        
        # Create minimal config
        config = {
            'deployment_type': 'minimal',
            'qa_data_available': True,
            'documents_available': False,
            'hybrid_mode': False,
            'setup_complete': True
        }
        
        with open('hybrid_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info("✅ Minimal deployment setup complete!")
        logger.info("   - QA data: Available")
        logger.info("   - Documents: Not included")
        logger.info("   - Total size: ~100MB")
        return True
    
    def setup_standard_deployment(self) -> bool:
        """
        Standard deployment: QA data + documents
        - Balanced setup
        - Medium footprint
        - Comprehensive coverage
        """
        logger.info("Setting up standard deployment (QA data + documents)...")
        
        # Check if QA data exists
        if not self.qa_data_path.exists():
            logger.error("QA data file not found. Please run comprehensive_qa_generator.py first.")
            return False
        
        # Check if document vector database exists
        doc_vector_db = self.base_dir / "vector_db"
        if not doc_vector_db.exists():
            logger.warning("Document vector database not found. Run vector_db_setup.py first.")
            logger.info("Continuing with QA data only...")
            return self.setup_minimal_deployment()
        
        # Create QA vector database
        if not self.create_qa_vector_db(str(self.qa_data_path)):
            return False
        
        # Create standard config
        config = {
            'deployment_type': 'standard',
            'qa_data_available': True,
            'documents_available': True,
            'hybrid_mode': True,
            'setup_complete': True
        }
        
        with open('hybrid_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info("✅ Standard deployment setup complete!")
        logger.info("   - QA data: Available")
        logger.info("   - Documents: Available")
        logger.info("   - Total size: ~200MB")
        return True
    
    def setup_full_deployment(self) -> bool:
        """
        Full deployment: Everything
        - Complete setup
        - Largest footprint
        - Maximum coverage
        """
        logger.info("Setting up full deployment (everything)...")
        
        # Check all components
        if not self.qa_data_path.exists():
            logger.error("QA data file not found. Please run comprehensive_qa_generator.py first.")
            return False
        
        doc_vector_db = self.base_dir / "vector_db"
        if not doc_vector_db.exists():
            logger.error("Document vector database not found. Run vector_db_setup.py first.")
            return False
        
        # Create QA vector database
        if not self.create_qa_vector_db(str(self.qa_data_path)):
            return False
        
        # Create full config
        config = {
            'deployment_type': 'full',
            'qa_data_available': True,
            'documents_available': True,
            'hybrid_mode': True,
            'setup_complete': True
        }
        
        with open('hybrid_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info("✅ Full deployment setup complete!")
        logger.info("   - QA data: Available")
        logger.info("   - Documents: Available")
        logger.info("   - Total size: ~300MB")
        return True
    
    def get_deployment_recommendation(self) -> str:
        """Get deployment recommendation based on available resources"""
        # Check available disk space
        try:
            stat = os.statvfs('.')
            free_space_gb = (stat.f_frsize * stat.f_bavail) / (1024**3)
            
            if free_space_gb < 1:
                return "minimal"
            elif free_space_gb < 2:
                return "standard"
            else:
                return "full"
        except:
            return "standard"
    
    def show_deployment_options(self):
        """Show available deployment options"""
        print("\n" + "="*60)
        print("HYBRID RAG PIPELINE DEPLOYMENT OPTIONS")
        print("="*60)
        
        print("\n🎯 Deployment Types:")
        print("\n1. MINIMAL (Recommended for most users)")
        print("   ✅ QA data only")
        print("   ✅ Fastest setup (~100MB)")
        print("   ✅ High accuracy for covered topics")
        print("   ✅ Easy maintenance")
        print("   ❌ Limited coverage")
        
        print("\n2. STANDARD (Recommended for power users)")
        print("   ✅ QA data + documents")
        print("   ✅ Balanced performance (~200MB)")
        print("   ✅ Comprehensive coverage")
        print("   ✅ Hybrid search capability")
        print("   ⚠️  Requires document setup")
        
        print("\n3. FULL (For advanced users)")
        print("   ✅ Everything included")
        print("   ✅ Maximum coverage (~300MB)")
        print("   ✅ Best performance")
        print("   ⚠️  Largest footprint")
        print("   ⚠️  Requires all components")
        
        recommendation = self.get_deployment_recommendation()
        print(f"\n💡 Recommendation: {recommendation.upper()} deployment")
        
        print("\n" + "="*60)
    
    def check_prerequisites(self) -> Dict[str, bool]:
        """Check what's available for deployment"""
        status = {
            'qa_data': self.qa_data_path.exists(),
            'doc_vector_db': (self.base_dir / "vector_db").exists(),
            'model': (self.base_dir / "mistral-7b-instruct-v0.1.Q4_K_M.gguf").exists(),
            'sample_qa': self.sample_qa_path.exists()
        }
        
        return status
    
    def show_status(self):
        """Show current system status"""
        status = self.check_prerequisites()
        
        print("\n" + "="*60)
        print("SYSTEM STATUS")
        print("="*60)
        
        print(f"QA Data: {'✅ Available' if status['qa_data'] else '❌ Missing'}")
        print(f"Document Vector DB: {'✅ Available' if status['doc_vector_db'] else '❌ Missing'}")
        print(f"Model File: {'✅ Available' if status['model'] else '❌ Missing'}")
        print(f"Sample QA Data: {'✅ Available' if status['sample_qa'] else '❌ Missing'}")
        
        if status['qa_data']:
            with open(self.qa_data_path, 'r') as f:
                qa_data = json.load(f)
                print(f"QA Pairs: {qa_data['metadata']['total_qa_pairs']}")
        
        print("="*60)

def main():
    parser = argparse.ArgumentParser(description='Hybrid RAG Pipeline Setup')
    parser.add_argument('--type', choices=['minimal', 'standard', 'full', 'auto'],
                       default='auto', help='Deployment type')
    parser.add_argument('--status', action='store_true',
                       help='Show system status')
    parser.add_argument('--options', action='store_true',
                       help='Show deployment options')
    
    args = parser.parse_args()
    
    setup = HybridRAGSetup()
    
    if args.status:
        setup.show_status()
        return
    
    if args.options:
        setup.show_deployment_options()
        return
    
    # Determine deployment type
    if args.type == 'auto':
        status = setup.check_prerequisites()
        if status['qa_data'] and status['doc_vector_db']:
            deployment_type = 'full'
        elif status['qa_data']:
            deployment_type = 'minimal'
        else:
            deployment_type = 'minimal'
    else:
        deployment_type = args.type
    
    # Show options if auto-selected
    if args.type == 'auto':
        setup.show_deployment_options()
        print(f"\n🤖 Auto-selected: {deployment_type.upper()} deployment")
        response = input("\nProceed? (y/n): ").lower().strip()
        if response != 'y':
            print("Setup cancelled.")
            return
    
    # Run setup
    success = False
    if deployment_type == 'minimal':
        success = setup.setup_minimal_deployment()
    elif deployment_type == 'standard':
        success = setup.setup_standard_deployment()
    elif deployment_type == 'full':
        success = setup.setup_full_deployment()
    
    if success:
        print("\n🚀 Setup complete! You can now run:")
        print("python hybrid_rag_pipeline.py")
    else:
        print("\n❌ Setup failed. Check the logs above.")

if __name__ == "__main__":
    main() 