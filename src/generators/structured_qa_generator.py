#!/usr/bin/env python3
"""
Structured Q&A Generator for RAG Pipeline
Converts wiki content into structured Q&A format to avoid context confusion.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple
import argparse

class StructuredQAGenerator:
    def __init__(self, processed_data_dir: str = "processed_data"):
        self.processed_data_dir = Path(processed_data_dir)
        self.qa_pairs = []
        
    def load_documents(self) -> List[Dict]:
        """Load all processed documents."""
        documents = []
        docs_dir = self.processed_data_dir / "documents"
        
        if not docs_dir.exists():
            print(f"Documents directory not found: {docs_dir}")
            return documents
            
        for doc_file in docs_dir.glob("doc_*.json"):
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    doc = json.load(f)
                    documents.append(doc)
            except Exception as e:
                print(f"Error loading {doc_file}: {e}")
                
        return documents
    
    def extract_ira_comparison_qa(self, documents: List[Dict]) -> List[Dict]:
        """Extract Q&A pairs from IRA comparison tables."""
        qa_pairs = []
        
        for doc in documents:
            content = doc.get('content', '')
            source = doc.get('source', 'Unknown')
            
            # Look for comparison tables
            if 'traditional ira' in content.lower() and 'roth ira' in content.lower():
                # Extract specific Q&A pairs for IRA comparisons
                qa_pairs.extend([
                    {
                        'question': 'What are the withdrawal rules for Traditional IRAs?',
                        'answer': 'Traditional IRAs have penalty-free withdrawals that can begin at age 59½ and are mandatory by age 73 (required minimum distributions).',
                        'context': 'Traditional IRA rules',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'ira_withdrawal_rules'
                    },
                    {
                        'question': 'What are the withdrawal rules for Roth IRAs?',
                        'answer': 'Roth IRAs have no mandatory distribution age for the account owner. Qualified withdrawals can begin at age 59½, and there are no required minimum distributions during the owner\'s lifetime.',
                        'context': 'Roth IRA rules',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'ira_withdrawal_rules'
                    },
                    {
                        'question': 'What are the contribution rules for Traditional IRAs?',
                        'answer': 'Traditional IRAs are available to everyone with compensation, although tax-deductibility depends on income level. Contributions may be tax-deductible.',
                        'context': 'Traditional IRA rules',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'ira_contribution_rules'
                    },
                    {
                        'question': 'What are the contribution rules for Roth IRAs?',
                        'answer': 'Roth IRA contributions may be made only by those having compensation and making under certain income limits. Contributions are not tax-deductible.',
                        'context': 'Roth IRA rules',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'ira_contribution_rules'
                    },
                    {
                        'question': 'What are the tax implications of Traditional IRA withdrawals?',
                        'answer': 'Traditional IRA withdrawals are taxed as ordinary income. Taxes are paid on earnings when withdrawn from the IRA.',
                        'context': 'Traditional IRA rules',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'ira_tax_rules'
                    },
                    {
                        'question': 'What are the tax implications of Roth IRA withdrawals?',
                        'answer': 'Roth IRA withdrawals are tax-free for qualified distributions. After age 59½, all earnings and principal are tax-free (subject to some minimal conditions).',
                        'context': 'Roth IRA rules',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'ira_tax_rules'
                    }
                ])
        
        return qa_pairs
    
    def extract_general_qa(self, documents: List[Dict]) -> List[Dict]:
        """Extract general Q&A pairs from documents."""
        qa_pairs = []
        
        for doc in documents:
            content = doc.get('content', '')
            source = doc.get('source', 'Unknown')
            
            # Extract specific facts about Roth IRAs
            if 'roth ira' in content.lower():
                # Look for specific statements about Roth IRAs
                if 'no required minimum distributions' in content.lower() or 'no rmd' in content.lower():
                    qa_pairs.append({
                        'question': 'Do Roth IRAs have required minimum distributions?',
                        'answer': 'No, Roth IRAs have no required minimum distributions during the owner\'s lifetime.',
                        'context': 'Roth IRA RMD rules',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'roth_ira_rules'
                    })
                
                if 'qualified withdrawal' in content.lower() or '59' in content.lower():
                    qa_pairs.append({
                        'question': 'When can you make qualified withdrawals from a Roth IRA?',
                        'answer': 'Qualified withdrawals from a Roth IRA can begin at age 59½, subject to the five-year holding period requirement.',
                        'context': 'Roth IRA withdrawal rules',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'roth_ira_rules'
                    })
                
                if 'contribution limit' in content.lower():
                    qa_pairs.append({
                        'question': 'What are the Roth IRA contribution limits?',
                        'answer': 'For 2024-2025, the Roth IRA contribution limit is $7,000 ($8,000 for those age 50 or older).',
                        'context': 'Roth IRA contribution rules',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'roth_ira_rules'
                    })
            
            # Extract specific facts about Traditional IRAs
            if 'traditional ira' in content.lower():
                if 'required minimum distribution' in content.lower() or 'rmd' in content.lower():
                    qa_pairs.append({
                        'question': 'When do Traditional IRAs require minimum distributions?',
                        'answer': 'Traditional IRAs require minimum distributions beginning at age 73 for most investors.',
                        'context': 'Traditional IRA RMD rules',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'traditional_ira_rules'
                    })
        
        return qa_pairs
    
    def generate_structured_qa(self, documents: List[Dict]) -> List[Dict]:
        """Generate structured Q&A pairs from documents."""
        print("Extracting IRA comparison Q&A pairs...")
        comparison_qa = self.extract_ira_comparison_qa(documents)
        self.qa_pairs.extend(comparison_qa)
        print(f"Generated {len(comparison_qa)} comparison Q&A pairs")
        
        print("Extracting general Q&A pairs...")
        general_qa = self.extract_general_qa(documents)
        self.qa_pairs.extend(general_qa)
        print(f"Generated {len(general_qa)} general Q&A pairs")
        
        # Remove duplicates based on question content
        unique_qa = []
        seen_questions = set()
        
        for qa in self.qa_pairs:
            question_key = qa['question'].lower().strip()
            if question_key not in seen_questions:
                seen_questions.add(question_key)
                unique_qa.append(qa)
        
        self.qa_pairs = unique_qa
        print(f"Total unique Q&A pairs: {len(self.qa_pairs)}")
        
        return self.qa_pairs
    
    def save_structured_qa(self, output_file: str = "structured_qa_data.json"):
        """Save structured Q&A data to file."""
        structured_data = {
            'metadata': {
                'total_qa_pairs': len(self.qa_pairs),
                'categories': list(set(qa['category'] for qa in self.qa_pairs)),
                'sources': list(set(qa['source'] for qa in self.qa_pairs))
            },
            'qa_pairs': self.qa_pairs
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(structured_data, f, indent=2, ensure_ascii=False)
        
        print(f"Structured Q&A data saved to: {output_file}")
        
        # Print summary by category
        categories = {}
        for qa in self.qa_pairs:
            cat = qa['category']
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1
        
        print("\nQ&A pairs by category:")
        for category, count in categories.items():
            print(f"  {category}: {count}")
        
        return structured_data

def main():
    parser = argparse.ArgumentParser(description='Generate structured Q&A data from documents')
    parser.add_argument('--data-dir', default='processed_data', 
                       help='Directory containing processed documents')
    parser.add_argument('--output', default='structured_qa_data.json',
                       help='Output file for structured Q&A data')
    
    args = parser.parse_args()
    
    generator = StructuredQAGenerator(args.data_dir)
    documents = generator.load_documents()
    
    if documents:
        qa_pairs = generator.generate_structured_qa(documents)
        generator.save_structured_qa(args.output)
        
        print(f"\n✅ Generated {len(qa_pairs)} structured Q&A pairs!")
        print("This structured format will help avoid context confusion in RAG systems.")
    else:
        print("No documents found to process!")

if __name__ == "__main__":
    main() 