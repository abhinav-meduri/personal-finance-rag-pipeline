#!/usr/bin/env python3
"""
Q&A Content Manager
Manages, validates, and curates structured Q&A content for the RAG pipeline.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Set, Optional
import argparse
from datetime import datetime
import difflib

class QAContentManager:
    def __init__(self, qa_data_file: str = "comprehensive_qa_data.json"):
        self.qa_data_file = qa_data_file
        self.qa_data = None
        self.backup_dir = Path("qa_backups")
        self.backup_dir.mkdir(exist_ok=True)
        
    def load_qa_data(self) -> Dict:
        """Load Q&A data from file."""
        if not os.path.exists(self.qa_data_file):
            print(f"Q&A data file not found: {self.qa_data_file}")
            return {}
            
        with open(self.qa_data_file, 'r', encoding='utf-8') as f:
            self.qa_data = json.load(f)
            
        print(f"Loaded {self.qa_data['metadata']['total_qa_pairs']} Q&A pairs")
        return self.qa_data
    
    def save_qa_data(self, output_file: str = None):
        """Save Q&A data to file with backup."""
        if output_file is None:
            output_file = self.qa_data_file
        
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"qa_backup_{timestamp}.json"
        
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(current_data, f, indent=2, ensure_ascii=False)
            print(f"Created backup: {backup_file}")
        
        # Save new data
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.qa_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved Q&A data to: {output_file}")
    
    def add_qa_pair(self, question: str, answer: str, context: str, 
                   category: str, source: str = "Manual", confidence: str = "high"):
        """Add a new Q&A pair."""
        if not self.qa_data:
            self.load_qa_data()
        
        qa_pair = {
            'question': question,
            'answer': answer,
            'context': context,
            'source': source,
            'doc_id': 'manual',
            'category': category,
            'confidence': confidence,
            'added_date': datetime.now().isoformat()
        }
        
        self.qa_data['qa_pairs'].append(qa_pair)
        self.qa_data['metadata']['total_qa_pairs'] += 1
        
        # Update category
        if category not in self.qa_data['categories']:
            self.qa_data['categories'][category] = []
        self.qa_data['categories'][category].append(qa_pair)
        
        # Update metadata
        if category not in self.qa_data['metadata']['categories']:
            self.qa_data['metadata']['categories'].append(category)
        if source not in self.qa_data['metadata']['sources']:
            self.qa_data['metadata']['sources'].append(source)
        
        print(f"✅ Added Q&A pair to category: {category}")
        return qa_pair
    
    def update_qa_pair(self, question: str, new_answer: str = None, new_context: str = None, 
                      new_category: str = None, new_confidence: str = None):
        """Update an existing Q&A pair."""
        if not self.qa_data:
            self.load_qa_data()
        
        for qa_pair in self.qa_data['qa_pairs']:
            if qa_pair['question'].lower().strip() == question.lower().strip():
                old_answer = qa_pair['answer']
                old_category = qa_pair['category']
                
                if new_answer:
                    qa_pair['answer'] = new_answer
                if new_context:
                    qa_pair['context'] = new_context
                if new_category:
                    qa_pair['category'] = new_category
                if new_confidence:
                    qa_pair['confidence'] = new_confidence
                
                qa_pair['updated_date'] = datetime.now().isoformat()
                
                # Update category lists
                if new_category and new_category != old_category:
                    # Remove from old category
                    self.qa_data['categories'][old_category] = [
                        qa for qa in self.qa_data['categories'][old_category] 
                        if qa['question'] != qa_pair['question']
                    ]
                    # Add to new category
                    if new_category not in self.qa_data['categories']:
                        self.qa_data['categories'][new_category] = []
                    self.qa_data['categories'][new_category].append(qa_pair)
                
                print(f"✅ Updated Q&A pair: {question}")
                if new_answer:
                    print(f"   Old answer: {old_answer}")
                    print(f"   New answer: {new_answer}")
                return qa_pair
        
        print(f"❌ Q&A pair not found: {question}")
        return None
    
    def delete_qa_pair(self, question: str):
        """Delete a Q&A pair."""
        if not self.qa_data:
            self.load_qa_data()
        
        for i, qa_pair in enumerate(self.qa_data['qa_pairs']):
            if qa_pair['question'].lower().strip() == question.lower().strip():
                category = qa_pair['category']
                
                # Remove from main list
                del self.qa_data['qa_pairs'][i]
                self.qa_data['metadata']['total_qa_pairs'] -= 1
                
                # Remove from category
                self.qa_data['categories'][category] = [
                    qa for qa in self.qa_data['categories'][category] 
                    if qa['question'] != qa_pair['question']
                ]
                
                print(f"✅ Deleted Q&A pair: {question}")
                return True
        
        print(f"❌ Q&A pair not found: {question}")
        return False
    
    def search_qa_pairs(self, query: str, category: str = None) -> List[Dict]:
        """Search Q&A pairs by question or answer content."""
        if not self.qa_data:
            self.load_qa_data()
        
        results = []
        query_lower = query.lower()
        
        for qa_pair in self.qa_data['qa_pairs']:
            if category and qa_pair['category'] != category:
                continue
                
            if (query_lower in qa_pair['question'].lower() or 
                query_lower in qa_pair['answer'].lower()):
                results.append(qa_pair)
        
        return results
    
    def validate_qa_pairs(self) -> Dict:
        """Validate Q&A pairs for consistency and completeness."""
        if not self.qa_data:
            self.load_qa_data()
        
        issues = {
            'missing_fields': [],
            'duplicate_questions': [],
            'empty_answers': [],
            'low_confidence': [],
            'orphaned_categories': []
        }
        
        seen_questions = set()
        
        for qa_pair in self.qa_data['qa_pairs']:
            # Check for missing fields
            required_fields = ['question', 'answer', 'context', 'category', 'source']
            for field in required_fields:
                if field not in qa_pair or not qa_pair[field]:
                    issues['missing_fields'].append({
                        'qa_pair': qa_pair,
                        'missing_field': field
                    })
            
            # Check for duplicate questions
            question_key = qa_pair['question'].lower().strip()
            if question_key in seen_questions:
                issues['duplicate_questions'].append(qa_pair)
            else:
                seen_questions.add(question_key)
            
            # Check for empty answers
            if not qa_pair.get('answer', '').strip():
                issues['empty_answers'].append(qa_pair)
            
            # Check for low confidence
            if qa_pair.get('confidence') == 'low':
                issues['low_confidence'].append(qa_pair)
        
        # Check for orphaned categories
        for category in self.qa_data['categories']:
            if not self.qa_data['categories'][category]:
                issues['orphaned_categories'].append(category)
        
        return issues
    
    def export_category(self, category: str, output_file: str = None):
        """Export Q&A pairs for a specific category."""
        if not self.qa_data:
            self.load_qa_data()
        
        if category not in self.qa_data['categories']:
            print(f"Category '{category}' not found")
            return
        
        qa_list = self.qa_data['categories'][category]
        if output_file is None:
            output_file = f"{category}_qa_data.json"
        
        category_data = {
            'category': category,
            'qa_pairs': qa_list,
            'count': len(qa_list),
            'export_date': datetime.now().isoformat()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(category_data, f, indent=2, ensure_ascii=False)
        
        print(f"Exported {len(qa_list)} Q&A pairs to: {output_file}")
    
    def import_category(self, import_file: str, category: str = None):
        """Import Q&A pairs from a file."""
        if not os.path.exists(import_file):
            print(f"Import file not found: {import_file}")
            return
        
        with open(import_file, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        
        if not self.qa_data:
            self.load_qa_data()
        
        imported_count = 0
        for qa_pair in import_data.get('qa_pairs', []):
            if category:
                qa_pair['category'] = category
            
            # Add to main list
            self.qa_data['qa_pairs'].append(qa_pair)
            self.qa_data['metadata']['total_qa_pairs'] += 1
            
            # Add to category
            cat = qa_pair['category']
            if cat not in self.qa_data['categories']:
                self.qa_data['categories'][cat] = []
            self.qa_data['categories'][cat].append(qa_pair)
            
            # Update metadata
            if cat not in self.qa_data['metadata']['categories']:
                self.qa_data['metadata']['categories'].append(cat)
            if qa_pair['source'] not in self.qa_data['metadata']['sources']:
                self.qa_data['metadata']['sources'].append(qa_pair['source'])
            
            imported_count += 1
        
        print(f"✅ Imported {imported_count} Q&A pairs from: {import_file}")
    
    def generate_report(self) -> Dict:
        """Generate a comprehensive report of the Q&A knowledge base."""
        if not self.qa_data:
            self.load_qa_data()
        
        report = {
            'summary': {
                'total_qa_pairs': self.qa_data['metadata']['total_qa_pairs'],
                'categories': len(self.qa_data['metadata']['categories']),
                'sources': len(self.qa_data['metadata']['sources']),
                'last_updated': datetime.now().isoformat()
            },
            'category_breakdown': {},
            'source_breakdown': {},
            'confidence_breakdown': {},
            'validation_issues': self.validate_qa_pairs()
        }
        
        # Category breakdown
        for category, qa_list in self.qa_data['categories'].items():
            report['category_breakdown'][category] = len(qa_list)
        
        # Source breakdown
        source_counts = {}
        for qa_pair in self.qa_data['qa_pairs']:
            source = qa_pair['source']
            source_counts[source] = source_counts.get(source, 0) + 1
        report['source_breakdown'] = source_counts
        
        # Confidence breakdown
        confidence_counts = {}
        for qa_pair in self.qa_data['qa_pairs']:
            confidence = qa_pair.get('confidence', 'unknown')
            confidence_counts[confidence] = confidence_counts.get(confidence, 0) + 1
        report['confidence_breakdown'] = confidence_counts
        
        return report
    
    def interactive_mode(self):
        """Run interactive content management mode."""
        print("\n🎯 Q&A Content Manager - Interactive Mode")
        print("Commands: add, update, delete, search, validate, export, report, quit")
        print("-" * 50)
        
        while True:
            try:
                command = input("\n💬 Command: ").strip().lower()
                
                if command == 'quit':
                    break
                elif command == 'add':
                    self.interactive_add()
                elif command == 'update':
                    self.interactive_update()
                elif command == 'delete':
                    self.interactive_delete()
                elif command == 'search':
                    self.interactive_search()
                elif command == 'validate':
                    self.interactive_validate()
                elif command == 'export':
                    self.interactive_export()
                elif command == 'report':
                    self.interactive_report()
                else:
                    print("Unknown command. Type 'quit' to exit.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def interactive_add(self):
        """Interactive add Q&A pair."""
        print("\n📝 Adding new Q&A pair:")
        question = input("Question: ").strip()
        answer = input("Answer: ").strip()
        context = input("Context: ").strip()
        category = input("Category: ").strip()
        source = input("Source (default: Manual): ").strip() or "Manual"
        confidence = input("Confidence (high/medium/low, default: high): ").strip() or "high"
        
        if question and answer and context and category:
            self.add_qa_pair(question, answer, context, category, source, confidence)
            self.save_qa_data()
        else:
            print("❌ Question, answer, context, and category are required!")
    
    def interactive_update(self):
        """Interactive update Q&A pair."""
        question = input("Question to update: ").strip()
        if not question:
            return
        
        results = self.search_qa_pairs(question)
        if not results:
            print("❌ Question not found!")
            return
        
        if len(results) > 1:
            print("Multiple matches found:")
            for i, result in enumerate(results):
                print(f"{i+1}. {result['question']}")
            choice = input("Select number: ").strip()
            try:
                qa_pair = results[int(choice) - 1]
            except:
                print("❌ Invalid choice!")
                return
        else:
            qa_pair = results[0]
        
        print(f"\nUpdating: {qa_pair['question']}")
        new_answer = input(f"New answer (current: {qa_pair['answer']}): ").strip()
        new_context = input(f"New context (current: {qa_pair['context']}): ").strip()
        new_category = input(f"New category (current: {qa_pair['category']}): ").strip()
        
        self.update_qa_pair(
            qa_pair['question'],
            new_answer if new_answer else None,
            new_context if new_context else None,
            new_category if new_category else None
        )
        self.save_qa_data()
    
    def interactive_search(self):
        """Interactive search Q&A pairs."""
        query = input("Search query: ").strip()
        category = input("Category filter (optional): ").strip() or None
        
        results = self.search_qa_pairs(query, category)
        print(f"\nFound {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['question']}")
            print(f"   Answer: {result['answer'][:100]}...")
            print(f"   Category: {result['category']}")
            print()
    
    def interactive_validate(self):
        """Interactive validation."""
        issues = self.validate_qa_pairs()
        print("\n🔍 Validation Results:")
        
        for issue_type, issue_list in issues.items():
            if issue_list:
                print(f"\n❌ {issue_type.replace('_', ' ').title()}: {len(issue_list)}")
                for issue in issue_list[:3]:  # Show first 3
                    if isinstance(issue, dict):
                        print(f"   - {issue.get('qa_pair', {}).get('question', 'Unknown')}")
                    else:
                        print(f"   - {issue.get('question', 'Unknown')}")
                if len(issue_list) > 3:
                    print(f"   ... and {len(issue_list) - 3} more")
            else:
                print(f"✅ {issue_type.replace('_', ' ').title()}: OK")
    
    def interactive_export(self):
        """Interactive export."""
        print("\nAvailable categories:")
        for category in self.qa_data['metadata']['categories']:
            count = len(self.qa_data['categories'][category])
            print(f"  • {category}: {count} Q&A pairs")
        
        category = input("Category to export: ").strip()
        if category:
            self.export_category(category)
    
    def interactive_report(self):
        """Interactive report generation."""
        report = self.generate_report()
        print("\n📊 Q&A Knowledge Base Report:")
        print(f"Total Q&A pairs: {report['summary']['total_qa_pairs']}")
        print(f"Categories: {report['summary']['categories']}")
        print(f"Sources: {report['summary']['sources']}")
        
        print("\n📂 Category Breakdown:")
        for category, count in report['category_breakdown'].items():
            print(f"  • {category}: {count}")
        
        print("\n📚 Source Breakdown:")
        for source, count in report['source_breakdown'].items():
            print(f"  • {source}: {count}")
        
        print("\n🎯 Confidence Breakdown:")
        for confidence, count in report['confidence_breakdown'].items():
            print(f"  • {confidence}: {count}")

def main():
    parser = argparse.ArgumentParser(description='Q&A Content Manager')
    parser.add_argument('--qa-file', default='comprehensive_qa_data.json',
                       help='Q&A data file to manage')
    parser.add_argument('--add', action='store_true',
                       help='Add a new Q&A pair')
    parser.add_argument('--update', type=str,
                       help='Update Q&A pair with question')
    parser.add_argument('--delete', type=str,
                       help='Delete Q&A pair with question')
    parser.add_argument('--search', type=str,
                       help='Search Q&A pairs')
    parser.add_argument('--validate', action='store_true',
                       help='Validate Q&A pairs')
    parser.add_argument('--export', type=str,
                       help='Export category')
    parser.add_argument('--report', action='store_true',
                       help='Generate report')
    parser.add_argument('--interactive', action='store_true',
                       help='Run interactive mode')
    
    args = parser.parse_args()
    
    manager = QAContentManager(args.qa_file)
    
    if args.interactive:
        manager.interactive_mode()
    elif args.add:
        manager.interactive_add()
    elif args.update:
        manager.interactive_update()
    elif args.delete:
        manager.delete_qa_pair(args.delete)
        manager.save_qa_data()
    elif args.search:
        results = manager.search_qa_pairs(args.search)
        print(f"Found {len(results)} results")
        for result in results:
            print(f"- {result['question']}")
    elif args.validate:
        issues = manager.validate_qa_pairs()
        print("Validation complete. Check issues.")
    elif args.export:
        manager.export_category(args.export)
    elif args.report:
        report = manager.generate_report()
        print(json.dumps(report, indent=2))
    else:
        print("Use --interactive for interactive mode or specify an action.")

if __name__ == "__main__":
    main() 