#!/usr/bin/env python3
"""
Google Doc Processor for RAG Pipeline
Processes Google Docs and integrates them into the RAG system.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse
import re
from datetime import datetime

class GoogleDocProcessor:
    """Process Google Docs for RAG pipeline integration"""
    
    def __init__(self, output_dir: str = "processed_docs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def process_text_content(self, content: str, title: str = "Financial Advice for a 20-year-old") -> Dict[str, Any]:
        """Process text content from Google Doc"""
        
        # Clean and structure the content
        cleaned_content = self._clean_content(content)
        
        # Extract Q&A pairs
        qa_pairs = self._extract_qa_pairs(cleaned_content, title)
        
        # Create document chunks
        document_chunks = self._create_document_chunks(cleaned_content, title)
        
        return {
            'title': title,
            'original_content': content,
            'cleaned_content': cleaned_content,
            'qa_pairs': qa_pairs,
            'document_chunks': document_chunks,
            'metadata': {
                'source': 'Google Doc',
                'title': title,
                'processed_date': datetime.now().isoformat(),
                'qa_count': len(qa_pairs),
                'chunk_count': len(document_chunks)
            }
        }
    
    def _clean_content(self, content: str) -> str:
        """Clean and structure the content"""
        # Remove extra whitespace
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = re.sub(r' +', ' ', content)
        
        # Remove common Google Doc artifacts
        content = re.sub(r'\[.*?\]', '', content)  # Remove brackets
        content = re.sub(r'Page \d+', '', content)  # Remove page numbers
        
        return content.strip()
    
    def _extract_qa_pairs(self, content: str, title: str) -> List[Dict[str, Any]]:
        """Extract Q&A pairs from the content"""
        qa_pairs = []
        
        # Split content into sections
        sections = content.split('\n\n')
        
        for i, section in enumerate(sections):
            if len(section.strip()) < 50:  # Skip very short sections
                continue
                
            # Generate Q&A pairs from each section
            section_qa = self._generate_qa_from_section(section, title, i)
            qa_pairs.extend(section_qa)
        
        return qa_pairs
    
    def _generate_qa_from_section(self, section: str, title: str, section_id: int) -> List[Dict[str, Any]]:
        """Generate Q&A pairs from a content section"""
        qa_pairs = []
        
        # Extract key topics and create questions
        topics = self._extract_topics(section)
        
        for topic in topics:
            # Create question based on topic
            question = self._create_question_from_topic(topic)
            
            # Extract relevant answer from section
            answer = self._extract_answer_for_topic(section, topic)
            
            if answer and len(answer) > 20:  # Only include substantial answers
                qa_pairs.append({
                    'question': question,
                    'answer': answer,
                    'context': f"{title} - {topic}",
                    'source': title,
                    'doc_id': f"{title.lower().replace(' ', '_')}_{section_id}",
                    'category': self._categorize_topic(topic),
                    'confidence': 'high',
                    'metadata': {
                        'section_id': section_id,
                        'topic': topic,
                        'source_type': 'google_doc'
                    }
                })
        
        return qa_pairs
    
    def _extract_topics(self, section: str) -> List[str]:
        """Extract key topics from a section"""
        topics = []
        
        # Look for common financial topics
        financial_topics = [
            'budgeting', 'saving', 'investing', 'emergency fund', 'debt',
            'credit score', 'retirement', 'insurance', 'taxes', 'student loans',
            'credit cards', 'banking', 'financial goals', 'compound interest',
            'diversification', 'risk management', 'financial planning'
        ]
        
        section_lower = section.lower()
        for topic in financial_topics:
            if topic in section_lower:
                topics.append(topic)
        
        # Extract topics from headings (lines ending with :)
        lines = section.split('\n')
        for line in lines:
            if line.strip().endswith(':') and len(line.strip()) < 100:
                topic = line.strip()[:-1]  # Remove the colon
                topics.append(topic)
        
        return list(set(topics))  # Remove duplicates
    
    def _create_question_from_topic(self, topic: str) -> str:
        """Create a question based on a topic"""
        topic_lower = topic.lower()
        
        # Map topics to common questions
        question_templates = {
            'budgeting': f"How should a 20-year-old approach {topic}?",
            'saving': f"What are the best {topic} strategies for young adults?",
            'investing': f"How should a 20-year-old start {topic}?",
            'emergency fund': f"How much should a 20-year-old save in an {topic}?",
            'debt': f"How should a 20-year-old manage {topic}?",
            'credit score': f"How can a 20-year-old build a good {topic}?",
            'retirement': f"Why should a 20-year-old think about {topic}?",
            'insurance': f"What types of {topic} does a 20-year-old need?",
            'taxes': f"How should a 20-year-old handle {topic}?",
            'student loans': f"How should a 20-year-old manage {topic}?",
            'credit cards': f"How should a 20-year-old use {topic}?",
            'banking': f"What {topic} services should a 20-year-old use?",
            'financial goals': f"How should a 20-year-old set {topic}?",
            'compound interest': f"Why is {topic} important for young adults?",
            'diversification': f"Why is {topic} important in investing?",
            'risk management': f"How should a 20-year-old approach {topic}?",
            'financial planning': f"How should a 20-year-old start {topic}?"
        }
        
        # Find matching template
        for key, template in question_templates.items():
            if key in topic_lower:
                return template
        
        # Default template
        return f"What should a 20-year-old know about {topic}?"
    
    def _extract_answer_for_topic(self, section: str, topic: str) -> str:
        """Extract relevant answer for a topic from a section"""
        # Find sentences that mention the topic
        sentences = re.split(r'[.!?]+', section)
        relevant_sentences = []
        
        topic_lower = topic.lower()
        for sentence in sentences:
            if topic_lower in sentence.lower() and len(sentence.strip()) > 20:
                relevant_sentences.append(sentence.strip())
        
        if relevant_sentences:
            # Combine relevant sentences
            answer = '. '.join(relevant_sentences[:3])  # Limit to 3 sentences
            return answer + '.'
        
        # If no specific topic sentences, use the whole section
        return section[:500] + "..." if len(section) > 500 else section
    
    def _categorize_topic(self, topic: str) -> str:
        """Categorize a topic into a standard category"""
        topic_lower = topic.lower()
        
        categories = {
            'budgeting': 'financial_planning',
            'saving': 'saving_strategies',
            'investing': 'investment_basics',
            'emergency fund': 'emergency_fund',
            'debt': 'debt_management',
            'credit score': 'credit_management',
            'retirement': 'retirement_planning',
            'insurance': 'insurance_basics',
            'taxes': 'tax_planning',
            'student loans': 'student_loan_management',
            'credit cards': 'credit_card_management',
            'banking': 'banking_basics',
            'financial goals': 'financial_planning',
            'compound interest': 'investment_basics',
            'diversification': 'investment_basics',
            'risk management': 'risk_management',
            'financial planning': 'financial_planning'
        }
        
        for key, category in categories.items():
            if key in topic_lower:
                return category
        
        return 'general_financial_advice'
    
    def _create_document_chunks(self, content: str, title: str) -> List[Dict[str, Any]]:
        """Create document chunks for vector storage"""
        chunks = []
        
        # Split content into paragraphs
        paragraphs = content.split('\n\n')
        
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph.strip()) < 50:  # Skip very short paragraphs
                continue
            
            chunks.append({
                'content': paragraph.strip(),
                'metadata': {
                    'title': title,
                    'source': 'Google Doc',
                    'chunk_id': i,
                    'url': '',  # No URL for Google Doc
                    'section': f"Section {i+1}",
                    'source_type': 'google_doc'
                }
            })
        
        return chunks
    
    def save_qa_data(self, qa_pairs: List[Dict[str, Any]], filename: str = "google_doc_qa.json"):
        """Save Q&A pairs to file"""
        qa_data = {
            'metadata': {
                'total_qa_pairs': len(qa_pairs),
                'source': 'Google Doc',
                'processed_date': datetime.now().isoformat(),
                'categories': list(set(qa['category'] for qa in qa_pairs))
            },
            'qa_pairs': qa_pairs
        }
        
        output_file = self.output_dir / filename
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(qa_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved {len(qa_pairs)} Q&A pairs to {output_file}")
        return output_file
    
    def save_document_chunks(self, chunks: List[Dict[str, Any]], filename: str = "google_doc_chunks.json"):
        """Save document chunks to file"""
        output_file = self.output_dir / filename
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved {len(chunks)} document chunks to {output_file}")
        return output_file
    
    def merge_with_existing_qa(self, new_qa_pairs: List[Dict[str, Any]], existing_file: str = "comprehensive_qa_data.json"):
        """Merge new Q&A pairs with existing data"""
        if not os.path.exists(existing_file):
            print(f"⚠️  Existing Q&A file not found: {existing_file}")
            return self.save_qa_data(new_qa_pairs)
        
        # Load existing data
        with open(existing_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        
        # Add new Q&A pairs
        existing_data['qa_pairs'].extend(new_qa_pairs)
        
        # Update metadata
        existing_data['metadata']['total_qa_pairs'] = len(existing_data['qa_pairs'])
        
        # Add new categories
        new_categories = set(qa['category'] for qa in new_qa_pairs)
        existing_categories = set(existing_data['metadata']['categories'])
        existing_data['metadata']['categories'] = list(existing_categories.union(new_categories))
        
        # Save updated data
        with open(existing_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Merged {len(new_qa_pairs)} new Q&A pairs into {existing_file}")
        print(f"   Total Q&A pairs: {existing_data['metadata']['total_qa_pairs']}")
        return existing_file

def main():
    parser = argparse.ArgumentParser(description='Process Google Doc for RAG pipeline')
    parser.add_argument('--content', type=str, help='Text content from Google Doc')
    parser.add_argument('--file', type=str, help='File containing Google Doc content')
    parser.add_argument('--title', type=str, default='Financial Advice for a 20-year-old',
                       help='Title of the document')
    parser.add_argument('--merge', action='store_true',
                       help='Merge with existing Q&A data')
    parser.add_argument('--qa-only', action='store_true',
                       help='Generate only Q&A pairs (no document chunks)')
    parser.add_argument('--chunks-only', action='store_true',
                       help='Generate only document chunks (no Q&A pairs)')
    
    args = parser.parse_args()
    
    processor = GoogleDocProcessor()
    
    # Get content
    if args.content:
        content = args.content
    elif args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        print("❌ Please provide content via --content or --file")
        return
    
    # Process content
    print(f"🔍 Processing: {args.title}")
    result = processor.process_text_content(content, args.title)
    
    print(f"\n📊 Processing Results:")
    print(f"   Q&A Pairs: {len(result['qa_pairs'])}")
    print(f"   Document Chunks: {len(result['document_chunks'])}")
    
    # Save results
    if not args.chunks_only:
        if args.merge:
            processor.merge_with_existing_qa(result['qa_pairs'])
        else:
            processor.save_qa_data(result['qa_pairs'])
    
    if not args.qa_only:
        processor.save_document_chunks(result['document_chunks'])
    
    print(f"\n✅ Processing complete! Files saved to: {processor.output_dir}")

if __name__ == "__main__":
    main() 