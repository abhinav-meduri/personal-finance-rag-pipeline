#!/usr/bin/env python3
"""
Test Script for Bogleheads RAG Pipeline
Tests various components and functionality
"""

import json
import sys
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_data_preprocessing():
    """Test data preprocessing"""
    logger.info("Testing data preprocessing...")
    
    try:
        from data_preprocessor import BogleheadsDataPreprocessor
        
        preprocessor = BogleheadsDataPreprocessor()
        processed_docs = preprocessor.process_all_files()
        
        if processed_docs:
            logger.info(f"✓ Data preprocessing successful: {len(processed_docs)} documents processed")
            return True
        else:
            logger.error("✗ No documents were processed")
            return False
            
    except Exception as e:
        logger.error(f"✗ Data preprocessing failed: {e}")
        return False

def test_vector_db():
    """Test vector database functionality"""
    logger.info("Testing vector database...")
    
    try:
        from vector_db_setup import BogleheadsVectorDB
        
        vector_db = BogleheadsVectorDB()
        
        # Test search functionality
        test_query = "bond investing"
        results = vector_db.search_similar(test_query, k=3)
        
        if results:
            logger.info(f"✓ Vector database search successful: {len(results)} results found")
            return True
        else:
            logger.error("✗ No search results found")
            return False
            
    except Exception as e:
        logger.error(f"✗ Vector database test failed: {e}")
        return False

def test_rag_pipeline():
    """Test the complete RAG pipeline"""
    logger.info("Testing RAG pipeline...")
    
    try:
        from rag_pipeline import BogleheadsRAGPipeline
        
        # Initialize pipeline
        rag = BogleheadsRAGPipeline()
        
        # Test system info
        system_info = rag.get_system_info()
        logger.info(f"✓ System info retrieved: {system_info['total_documents']} documents")
        
        # Test document search
        search_results = rag.search_documents("investment basics", k=3)
        logger.info(f"✓ Document search successful: {len(search_results)} results")
        
        # Test question answering (with a simple question)
        test_question = "What are bonds?"
        result = rag.ask_question(test_question, k=3)
        
        if result and result['answer']:
            logger.info(f"✓ Question answering successful: {len(result['answer'])} characters")
            return True
        else:
            logger.error("✗ No answer generated")
            return False
            
    except Exception as e:
        logger.error(f"✗ RAG pipeline test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all tests"""
    print("="*60)
    print("BOGLEHEADS RAG PIPELINE - COMPREHENSIVE TEST")
    print("="*60)
    
    tests = [
        ("Data Preprocessing", test_data_preprocessing),
        ("Vector Database", test_vector_db),
        ("RAG Pipeline", test_rag_pipeline)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name} test...")
        try:
            success = test_func()
            results.append((test_name, success))
            status = "✓ PASSED" if success else "✗ FAILED"
            print(f"{test_name}: {status}")
        except Exception as e:
            results.append((test_name, False))
            print(f"{test_name}: ✗ FAILED - {e}")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your RAG pipeline is ready to use.")
        print("\nYou can now run:")
        print("python rag_pipeline.py")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1) 