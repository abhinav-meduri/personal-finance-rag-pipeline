#!/usr/bin/env python3
"""
Test RAG Comparison with predefined questions
"""

from rag_comparison import batch_comparison

# Predefined test questions
test_questions = [
    "What is a Roth IRA?",
    "How should I allocate my assets?",
    "What are the basics of bond investing?",
    "How do I start investing?",
    "What is the three-fund portfolio?",
    "What are the tax implications of different investment accounts?",
    "How do I choose between a traditional IRA and Roth IRA?",
    "What is asset allocation and why is it important?",
    "How do I calculate my retirement needs?",
    "What are the benefits of index funds?"
]

def main():
    print("="*60)
    print("RAG COMPARISON TEST")
    print("="*60)
    print(f"Testing {len(test_questions)} questions...")
    print("\nQuestions to test:")
    for i, question in enumerate(test_questions, 1):
        print(f"{i}. {question}")
    print("\n" + "="*60)
    
    # Run batch comparison
    results = batch_comparison(test_questions)
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    total_length_diff = 0
    total_sources = 0
    
    for i, result in enumerate(results, 1):
        analysis = result['analysis']
        total_length_diff += analysis['length_difference']
        total_sources += analysis['sources_count']
        
        print(f"{i}. {result['question'][:50]}...")
        print(f"   Length diff: {analysis['length_difference']:>6} chars")
        print(f"   Sources: {analysis['sources_count']}")
        
        if analysis['length_difference'] > 0:
            print("   ✅ RAG provided more detail")
        elif analysis['length_difference'] < 0:
            print("   ⚠️  RAG was more concise")
        else:
            print("   ➖ Same length")
        print()
    
    print(f"Average length difference: {total_length_diff / len(results):.1f} characters")
    print(f"Average sources used: {total_sources / len(results):.1f}")
    
    if total_length_diff > 0:
        print("✅ Overall: RAG provided more detailed answers")
    elif total_length_diff < 0:
        print("⚠️  Overall: RAG provided more concise answers")
    else:
        print("➖ Overall: No significant length difference")

if __name__ == "__main__":
    main() 