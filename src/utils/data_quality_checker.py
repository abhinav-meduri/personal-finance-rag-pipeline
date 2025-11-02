#!/usr/bin/env python3
"""
Data Quality Checker for RAG Pipeline
Identifies potential factual errors and inconsistencies in the knowledge base.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple
import argparse

class DataQualityChecker:
    def __init__(self, processed_data_dir: str = "processed_data"):
        self.processed_data_dir = Path(processed_data_dir)
        self.issues = []
        
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
    
    def check_roth_ira_errors(self, documents: List[Dict]) -> List[Dict]:
        """Check for common Roth IRA factual errors."""
        issues = []
        
        # Known incorrect statements about Roth IRAs
        incorrect_patterns = [
            r"mandatory.*73",  # Roth IRAs don't have mandatory distributions
            r"required.*distribution.*73",  # No RMDs for Roth IRAs
            r"Roth.*mandatory.*withdrawal",  # No mandatory withdrawals
            r"Roth.*RMD",  # Roth IRAs don't have RMDs
        ]
        
        # Correct statements that should be present
        correct_patterns = [
            r"Roth.*no.*RMD",  # Should mention no RMDs
            r"Roth.*no.*mandatory",  # Should mention no mandatory distributions
            r"Roth.*59.*1/2",  # Should mention age 59½ for qualified withdrawals
        ]
        
        for doc in documents:
            content = doc.get('content', '')
            source = doc.get('source', 'Unknown')
            
            # Check for incorrect statements
            for pattern in incorrect_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    issues.append({
                        'type': 'factual_error',
                        'category': 'roth_ira_rules',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'issue': f"Incorrect Roth IRA rule found: '{match.group()}'",
                        'context': content[max(0, match.start()-100):match.end()+100],
                        'severity': 'high',
                        'suggestion': 'Roth IRAs do not have required minimum distributions (RMDs)'
                    })
            
            # Check for missing correct statements in Roth IRA documents
            if 'roth' in content.lower() and 'ira' in content.lower():
                has_correct_info = any(re.search(pattern, content, re.IGNORECASE) 
                                     for pattern in correct_patterns)
                if not has_correct_info:
                    issues.append({
                        'type': 'missing_information',
                        'category': 'roth_ira_rules',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'issue': 'Roth IRA document missing key correct information',
                        'context': content[:200] + "...",
                        'severity': 'medium',
                        'suggestion': 'Should mention that Roth IRAs have no RMDs and qualified withdrawals start at age 59½'
                    })
        
        return issues
    
    def check_contradictions(self, documents: List[Dict]) -> List[Dict]:
        """Check for contradictory information across documents."""
        issues = []
        
        # Collect statements about key topics
        topic_statements = {}
        
        for doc in documents:
            content = doc.get('content', '')
            source = doc.get('source', 'Unknown')
            
            # Look for age-related statements
            age_matches = re.finditer(r'age\s+(\d+(?:\.\d+)?)', content, re.IGNORECASE)
            for match in age_matches:
                age = match.group(1)
                context = content[max(0, match.start()-50):match.end()+50]
                
                if 'roth' in content.lower() and 'ira' in content.lower():
                    key = f"roth_ira_age_{age}"
                    if key not in topic_statements:
                        topic_statements[key] = []
                    topic_statements[key].append({
                        'source': source,
                        'context': context,
                        'doc_id': doc.get('id', 'Unknown')
                    })
        
        # Check for contradictions
        for key, statements in topic_statements.items():
            if len(statements) > 1:
                # Check if different sources say different things about the same age
                contexts = [s['context'] for s in statements]
                if len(set(contexts)) > 1:
                    issues.append({
                        'type': 'contradiction',
                        'category': 'age_rules',
                        'source': 'multiple',
                        'doc_id': 'multiple',
                        'issue': f'Contradictory information about {key}',
                        'context': f'Found {len(statements)} different statements',
                        'severity': 'high',
                        'suggestion': 'Review and reconcile conflicting information',
                        'details': statements
                    })
        
        return issues
    
    def check_data_completeness(self, documents: List[Dict]) -> List[Dict]:
        """Check for incomplete or missing important information."""
        issues = []
        
        # Check for documents that mention Roth IRA but are very short
        for doc in documents:
            content = doc.get('content', '')
            if 'roth' in content.lower() and 'ira' in content.lower():
                if len(content) < 500:  # Very short Roth IRA document
                    issues.append({
                        'type': 'incomplete',
                        'category': 'content_length',
                        'source': doc.get('source', 'Unknown'),
                        'doc_id': doc.get('id', 'Unknown'),
                        'issue': 'Roth IRA document appears incomplete',
                        'context': content,
                        'severity': 'medium',
                        'suggestion': 'Document may need more comprehensive information'
                    })
        
        return issues
    
    def run_checks(self) -> List[Dict]:
        """Run all data quality checks."""
        print("Loading documents...")
        documents = self.load_documents()
        print(f"Loaded {len(documents)} documents")
        
        all_issues = []
        
        print("Checking for Roth IRA factual errors...")
        roth_issues = self.check_roth_ira_errors(documents)
        all_issues.extend(roth_issues)
        print(f"Found {len(roth_issues)} Roth IRA issues")
        
        print("Checking for contradictions...")
        contradiction_issues = self.check_contradictions(documents)
        all_issues.extend(contradiction_issues)
        print(f"Found {len(contradiction_issues)} contradiction issues")
        
        print("Checking data completeness...")
        completeness_issues = self.check_data_completeness(documents)
        all_issues.extend(completeness_issues)
        print(f"Found {len(completeness_issues)} completeness issues")
        
        return all_issues
    
    def generate_report(self, issues: List[Dict], output_file: str = "data_quality_report.json"):
        """Generate a detailed report of all issues found."""
        report = {
            'summary': {
                'total_issues': len(issues),
                'high_severity': len([i for i in issues if i['severity'] == 'high']),
                'medium_severity': len([i for i in issues if i['severity'] == 'medium']),
                'low_severity': len([i for i in issues if i['severity'] == 'low'])
            },
            'issues_by_type': {},
            'issues_by_category': {},
            'issues': issues
        }
        
        # Group by type
        for issue in issues:
            issue_type = issue['type']
            if issue_type not in report['issues_by_type']:
                report['issues_by_type'][issue_type] = []
            report['issues_by_type'][issue_type].append(issue)
        
        # Group by category
        for issue in issues:
            category = issue['category']
            if category not in report['issues_by_category']:
                report['issues_by_category'][category] = []
            report['issues_by_category'][category].append(issue)
        
        # Save report
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\nData Quality Report Summary:")
        print(f"Total issues found: {report['summary']['total_issues']}")
        print(f"High severity: {report['summary']['high_severity']}")
        print(f"Medium severity: {report['summary']['medium_severity']}")
        print(f"Low severity: {report['summary']['low_severity']}")
        print(f"\nDetailed report saved to: {output_file}")
        
        return report
    
    def suggest_fixes(self, issues: List[Dict]) -> List[Dict]:
        """Suggest specific fixes for the issues found."""
        fixes = []
        
        for issue in issues:
            if issue['type'] == 'factual_error' and 'roth_ira_rules' in issue['category']:
                fixes.append({
                    'issue_id': issue.get('doc_id', 'Unknown'),
                    'type': 'content_correction',
                    'description': f"Fix incorrect Roth IRA rule: {issue['issue']}",
                    'action': 'Replace incorrect statement with correct information',
                    'correct_text': 'Roth IRAs do not have required minimum distributions (RMDs). Qualified withdrawals can begin at age 59½.',
                    'priority': 'high'
                })
            elif issue['type'] == 'missing_information':
                fixes.append({
                    'issue_id': issue.get('doc_id', 'Unknown'),
                    'type': 'content_addition',
                    'description': f"Add missing Roth IRA information: {issue['issue']}",
                    'action': 'Add key Roth IRA rules to document',
                    'correct_text': 'Roth IRAs have no required minimum distributions during the owner\'s lifetime.',
                    'priority': 'medium'
                })
        
        return fixes

def main():
    parser = argparse.ArgumentParser(description='Check data quality for RAG pipeline')
    parser.add_argument('--data-dir', default='processed_data', 
                       help='Directory containing processed documents')
    parser.add_argument('--output', default='data_quality_report.json',
                       help='Output file for the quality report')
    parser.add_argument('--fixes', action='store_true',
                       help='Generate suggested fixes')
    
    args = parser.parse_args()
    
    checker = DataQualityChecker(args.data_dir)
    issues = checker.run_checks()
    
    if issues:
        report = checker.generate_report(issues, args.output)
        
        if args.fixes:
            fixes = checker.suggest_fixes(issues)
            fixes_file = args.output.replace('.json', '_fixes.json')
            with open(fixes_file, 'w', encoding='utf-8') as f:
                json.dump(fixes, f, indent=2, ensure_ascii=False)
            print(f"Suggested fixes saved to: {fixes_file}")
        
        # Print high severity issues
        high_issues = [i for i in issues if i['severity'] == 'high']
        if high_issues:
            print(f"\n=== HIGH SEVERITY ISSUES ===")
            for i, issue in enumerate(high_issues[:5], 1):  # Show first 5
                print(f"{i}. {issue['issue']}")
                print(f"   Source: {issue['source']}")
                print(f"   Suggestion: {issue['suggestion']}")
                print()
    else:
        print("No data quality issues found!")

if __name__ == "__main__":
    main() 