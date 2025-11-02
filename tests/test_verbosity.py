#!/usr/bin/env python3
"""
Test script to demonstrate verbosity control in the hybrid RAG pipeline.
"""

from hybrid_rag_pipeline import HybridRAGPipeline

def test_verbosity_levels():
    """Test both verbose and quiet modes"""
    
    print("="*60)
    print("TESTING VERBOSITY LEVELS")
    print("="*60)
    
    # Test quiet mode (default)
    print("\n1. QUIET MODE (default):")
    print("-" * 40)
    try:
        rag_quiet = HybridRAGPipeline(verbose=False)
        result = rag_quiet.ask_question("What is a Roth IRA?")
        print(f"Answer: {result['answer'][:100]}...")
        print(f"Method: {result['method']} (confidence: {result['confidence']})")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*60)
    print("2. VERBOSE MODE:")
    print("-" * 40)
    try:
        rag_verbose = HybridRAGPipeline(verbose=True)
        result = rag_verbose.ask_question("What is a Traditional IRA?")
        print(f"Answer: {result['answer'][:100]}...")
        print(f"Method: {result['method']} (confidence: {result['confidence']})")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_verbosity_levels() 