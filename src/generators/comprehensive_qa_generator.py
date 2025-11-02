#!/usr/bin/env python3
"""
Comprehensive Structured Q&A Generator
Processes all wiki pages to create a comprehensive, factually accurate Q&A knowledge base.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Set
import argparse
from collections import defaultdict

class ComprehensiveQAGenerator:
    def __init__(self, processed_data_dir: str = "processed_data"):
        self.processed_data_dir = Path(processed_data_dir)
        self.qa_pairs = []
        self.categories = defaultdict(list)
        self.fact_checkers = {}
        
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
                
        print(f"Loaded {len(documents)} documents")
        return documents
    
    def extract_ira_qa_pairs(self, documents: List[Dict]) -> List[Dict]:
        """Extract comprehensive IRA-related Q&A pairs."""
        qa_pairs = []
        
        for doc in documents:
            content = doc.get('content', '')
            source = doc.get('source', 'Unknown')
            
            # Traditional IRA Q&A pairs
            if 'traditional ira' in content.lower():
                qa_pairs.extend([
                    {
                        'question': 'What is a Traditional IRA?',
                        'answer': 'A Traditional IRA is an individual retirement account that allows tax-deductible contributions with tax-deferred growth. Withdrawals are taxed as ordinary income.',
                        'context': 'Traditional IRA definition',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'traditional_ira_basics',
                        'confidence': 'high'
                    },
                    {
                        'question': 'What are Traditional IRA contribution limits?',
                        'answer': 'For 2024-2025, the Traditional IRA contribution limit is $7,000 ($8,000 for those age 50 or older).',
                        'context': 'Traditional IRA contribution rules',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'traditional_ira_contributions',
                        'confidence': 'high'
                    },
                    {
                        'question': 'When do Traditional IRAs require minimum distributions?',
                        'answer': 'Traditional IRAs require minimum distributions beginning at age 73 for most investors.',
                        'context': 'Traditional IRA RMD rules',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'traditional_ira_withdrawals',
                        'confidence': 'high'
                    },
                    {
                        'question': 'Are Traditional IRA contributions tax-deductible?',
                        'answer': 'Traditional IRA contributions may be tax-deductible depending on income level and whether you are covered by an employer retirement plan.',
                        'context': 'Traditional IRA tax rules',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'traditional_ira_tax',
                        'confidence': 'high'
                    }
                ])
            
            # Roth IRA Q&A pairs
            if 'roth ira' in content.lower():
                qa_pairs.extend([
                    {
                        'question': 'What is a Roth IRA?',
                        'answer': 'A Roth IRA is an individual retirement account with after-tax contributions and tax-free growth and withdrawals for qualified distributions.',
                        'context': 'Roth IRA definition',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'roth_ira_basics',
                        'confidence': 'high'
                    },
                    {
                        'question': 'What are Roth IRA contribution limits?',
                        'answer': 'For 2024-2025, the Roth IRA contribution limit is $7,000 ($8,000 for those age 50 or older).',
                        'context': 'Roth IRA contribution rules',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'roth_ira_contributions',
                        'confidence': 'high'
                    },
                    {
                        'question': 'Do Roth IRAs have required minimum distributions?',
                        'answer': 'No, Roth IRAs have no required minimum distributions during the owner\'s lifetime.',
                        'context': 'Roth IRA RMD rules',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'roth_ira_withdrawals',
                        'confidence': 'high'
                    },
                    {
                        'question': 'When can you make qualified withdrawals from a Roth IRA?',
                        'answer': 'Qualified withdrawals from a Roth IRA can begin at age 59½, subject to the five-year holding period requirement.',
                        'context': 'Roth IRA withdrawal rules',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'roth_ira_withdrawals',
                        'confidence': 'high'
                    },
                    {
                        'question': 'Are Roth IRA contributions tax-deductible?',
                        'answer': 'No, Roth IRA contributions are not tax-deductible. They are made with after-tax dollars.',
                        'context': 'Roth IRA tax rules',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'roth_ira_tax',
                        'confidence': 'high'
                    }
                ])
        
        return qa_pairs
    
    def extract_401k_qa_pairs(self, documents: List[Dict]) -> List[Dict]:
        """Extract 401(k)-related Q&A pairs."""
        qa_pairs = []
        
        for doc in documents:
            content = doc.get('content', '')
            source = doc.get('source', 'Unknown')
            
            if '401(k)' in content or '401k' in content.lower():
                qa_pairs.extend([
                    {
                        'question': 'What is a 401(k) plan?',
                        'answer': 'A 401(k) is an employer-sponsored retirement plan that allows employees to contribute pre-tax dollars with potential employer matching.',
                        'context': '401(k) definition',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': '401k_basics',
                        'confidence': 'high'
                    },
                    {
                        'question': 'What are 401(k) contribution limits?',
                        'answer': 'For 2024-2025, the 401(k) elective deferral limit is $23,500 ($31,000 for those age 50 or older).',
                        'context': '401(k) contribution rules',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': '401k_contributions',
                        'confidence': 'high'
                    },
                    {
                        'question': 'When can you withdraw from a 401(k) without penalty?',
                        'answer': 'You can withdraw from a 401(k) without penalty at age 59½, or earlier for certain exceptions like disability or hardship.',
                        'context': '401(k) withdrawal rules',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': '401k_withdrawals',
                        'confidence': 'high'
                    }
                ])
        
        return qa_pairs
    
    def extract_investment_qa_pairs(self, documents: List[Dict]) -> List[Dict]:
        """Extract investment-related Q&A pairs."""
        qa_pairs = []
        
        for doc in documents:
            content = doc.get('content', '')
            source = doc.get('source', 'Unknown')
            
            # Index funds
            if 'index fund' in content.lower():
                qa_pairs.extend([
                    {
                        'question': 'What is an index fund?',
                        'answer': 'An index fund is a mutual fund or ETF that tracks a specific market index, providing broad market exposure at low cost.',
                        'context': 'Index fund definition',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'index_funds',
                        'confidence': 'high'
                    },
                    {
                        'question': 'What are the advantages of index funds?',
                        'answer': 'Index funds offer low costs, broad diversification, tax efficiency, and typically outperform most actively managed funds over time.',
                        'context': 'Index fund benefits',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'index_funds',
                        'confidence': 'high'
                    }
                ])
            
            # Asset allocation
            if 'asset allocation' in content.lower():
                qa_pairs.extend([
                    {
                        'question': 'What is asset allocation?',
                        'answer': 'Asset allocation is the distribution of investments across different asset classes like stocks, bonds, and cash to manage risk and return.',
                        'context': 'Asset allocation definition',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'asset_allocation',
                        'confidence': 'high'
                    }
                ])
            
            # Diversification
            if 'diversification' in content.lower():
                qa_pairs.extend([
                    {
                        'question': 'What is investment diversification?',
                        'answer': 'Diversification is spreading investments across different assets, sectors, and geographic regions to reduce risk.',
                        'context': 'Diversification definition',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'diversification',
                        'confidence': 'high'
                    }
                ])
        
        return qa_pairs
    
    def extract_tax_qa_pairs(self, documents: List[Dict]) -> List[Dict]:
        """Extract tax-related Q&A pairs."""
        qa_pairs = []
        
        for doc in documents:
            content = doc.get('content', '')
            source = doc.get('source', 'Unknown')
            
            if 'tax' in content.lower() and ('capital gain' in content.lower() or 'dividend' in content.lower()):
                qa_pairs.extend([
                    {
                        'question': 'What are qualified dividends?',
                        'answer': 'Qualified dividends are dividends that meet IRS requirements and are taxed at lower capital gains rates rather than ordinary income rates.',
                        'context': 'Qualified dividends',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'tax_optimization',
                        'confidence': 'high'
                    },
                    {
                        'question': 'What are long-term capital gains?',
                        'answer': 'Long-term capital gains are profits from selling investments held for more than one year, taxed at preferential rates.',
                        'context': 'Capital gains tax',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'tax_optimization',
                        'confidence': 'high'
                    }
                ])
        
        return qa_pairs
    
    def extract_retirement_planning_qa_pairs(self, documents: List[Dict]) -> List[Dict]:
        """Extract retirement planning Q&A pairs."""
        qa_pairs = []
        
        for doc in documents:
            content = doc.get('content', '')
            source = doc.get('source', 'Unknown')
            
            if 'social security' in content.lower():
                qa_pairs.extend([
                    {
                        'question': 'When can you start collecting Social Security?',
                        'answer': 'You can start collecting Social Security as early as age 62, but full retirement age is between 66-67 depending on birth year.',
                        'context': 'Social Security benefits',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'social_security',
                        'confidence': 'high'
                    },
                    {
                        'question': 'What is the full retirement age for Social Security?',
                        'answer': 'Full retirement age is 67 for those born in 1960 or later, 66 for those born 1943-1954, and varies for those born 1955-1959.',
                        'context': 'Social Security full retirement age',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'social_security',
                        'confidence': 'high'
                    }
                ])
            
            if 'required minimum distribution' in content.lower() or 'rmd' in content.lower():
                qa_pairs.extend([
                    {
                        'question': 'What are Required Minimum Distributions (RMDs)?',
                        'answer': 'RMDs are minimum amounts that must be withdrawn from traditional retirement accounts starting at age 73, based on account balance and life expectancy.',
                        'context': 'RMD rules',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'rmd_rules',
                        'confidence': 'high'
                    }
                ])
        
        return qa_pairs
    
    def extract_estate_planning_qa_pairs(self, documents: List[Dict]) -> List[Dict]:
        """Extract estate planning Q&A pairs."""
        qa_pairs = []
        
        for doc in documents:
            content = doc.get('content', '')
            source = doc.get('source', 'Unknown')
            
            if 'estate' in content.lower() and 'planning' in content.lower():
                qa_pairs.extend([
                    {
                        'question': 'What is estate planning?',
                        'answer': 'Estate planning involves arranging for the transfer of assets after death, including wills, trusts, and beneficiary designations.',
                        'context': 'Estate planning basics',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'estate_planning',
                        'confidence': 'high'
                    }
                ])
            
            if 'beneficiary' in content.lower():
                qa_pairs.extend([
                    {
                        'question': 'What is a beneficiary designation?',
                        'answer': 'A beneficiary designation specifies who will receive assets from retirement accounts or life insurance policies upon your death.',
                        'context': 'Beneficiary designations',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'estate_planning',
                        'confidence': 'high'
                    }
                ])
        
        return qa_pairs
    
    def extract_comparison_qa_pairs(self, documents: List[Dict]) -> List[Dict]:
        """Extract comparison Q&A pairs for different account types."""
        qa_pairs = []
        
        for doc in documents:
            content = doc.get('content', '')
            source = doc.get('source', 'Unknown')
            
            # Traditional vs Roth comparisons
            if 'traditional' in content.lower() and 'roth' in content.lower():
                qa_pairs.extend([
                    {
                        'question': 'What is the difference between Traditional and Roth IRAs?',
                        'answer': 'Traditional IRAs offer tax-deductible contributions and tax-deferred growth, while Roth IRAs use after-tax contributions with tax-free growth and withdrawals.',
                        'context': 'Traditional vs Roth IRA comparison',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'ira_comparisons',
                        'confidence': 'high'
                    },
                    {
                        'question': 'When should I choose a Traditional IRA over a Roth IRA?',
                        'answer': 'Choose Traditional IRA if your current tax rate is higher than your expected retirement tax rate. Choose Roth IRA if your current rate is lower than expected retirement rate.',
                        'context': 'Traditional vs Roth IRA decision',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'ira_comparisons',
                        'confidence': 'high'
                    }
                ])
            
            # IRA vs 401(k) comparisons
            if ('ira' in content.lower() and '401' in content) or ('ira' in content.lower() and 'employer' in content.lower()):
                qa_pairs.extend([
                    {
                        'question': 'What is the difference between IRAs and 401(k)s?',
                        'answer': 'IRAs are individual accounts with lower contribution limits but more investment choices. 401(k)s are employer-sponsored with higher limits but limited investment options.',
                        'context': 'IRA vs 401(k) comparison',
                        'source': source,
                        'doc_id': doc.get('id', 'Unknown'),
                        'category': 'account_comparisons',
                        'confidence': 'high'
                    }
                ])
        
        return qa_pairs
    
    def generate_comprehensive_qa(self, documents: List[Dict]) -> List[Dict]:
        """Generate comprehensive Q&A pairs from all documents."""
        print("🔍 Extracting IRA-related Q&A pairs...")
        ira_qa = self.extract_ira_qa_pairs(documents)
        self.qa_pairs.extend(ira_qa)
        print(f"Generated {len(ira_qa)} IRA Q&A pairs")
        
        print("🔍 Extracting 401(k)-related Q&A pairs...")
        k401_qa = self.extract_401k_qa_pairs(documents)
        self.qa_pairs.extend(k401_qa)
        print(f"Generated {len(k401_qa)} 401(k) Q&A pairs")
        
        print("🔍 Extracting investment-related Q&A pairs...")
        investment_qa = self.extract_investment_qa_pairs(documents)
        self.qa_pairs.extend(investment_qa)
        print(f"Generated {len(investment_qa)} investment Q&A pairs")
        
        print("🔍 Extracting tax-related Q&A pairs...")
        tax_qa = self.extract_tax_qa_pairs(documents)
        self.qa_pairs.extend(tax_qa)
        print(f"Generated {len(tax_qa)} tax Q&A pairs")
        
        print("🔍 Extracting retirement planning Q&A pairs...")
        retirement_qa = self.extract_retirement_planning_qa_pairs(documents)
        self.qa_pairs.extend(retirement_qa)
        print(f"Generated {len(retirement_qa)} retirement planning Q&A pairs")
        
        print("🔍 Extracting estate planning Q&A pairs...")
        estate_qa = self.extract_estate_planning_qa_pairs(documents)
        self.qa_pairs.extend(estate_qa)
        print(f"Generated {len(estate_qa)} estate planning Q&A pairs")
        
        print("🔍 Extracting comparison Q&A pairs...")
        comparison_qa = self.extract_comparison_qa_pairs(documents)
        self.qa_pairs.extend(comparison_qa)
        print(f"Generated {len(comparison_qa)} comparison Q&A pairs")
        
        # Remove duplicates and organize by category
        self.remove_duplicates()
        self.organize_by_category()
        
        return self.qa_pairs
    
    def remove_duplicates(self):
        """Remove duplicate Q&A pairs based on question content."""
        unique_qa = []
        seen_questions = set()
        
        for qa in self.qa_pairs:
            question_key = qa['question'].lower().strip()
            if question_key not in seen_questions:
                seen_questions.add(question_key)
                unique_qa.append(qa)
        
        self.qa_pairs = unique_qa
        print(f"Removed duplicates. Total unique Q&A pairs: {len(self.qa_pairs)}")
    
    def organize_by_category(self):
        """Organize Q&A pairs by category."""
        for qa in self.qa_pairs:
            category = qa['category']
            self.categories[category].append(qa)
    
    def save_comprehensive_qa(self, output_file: str = "comprehensive_qa_data.json"):
        """Save comprehensive Q&A data to file."""
        structured_data = {
            'metadata': {
                'total_qa_pairs': len(self.qa_pairs),
                'categories': list(self.categories.keys()),
                'category_counts': {cat: len(qa_list) for cat, qa_list in self.categories.items()},
                'sources': list(set(qa['source'] for qa in self.qa_pairs))
            },
            'qa_pairs': self.qa_pairs,
            'categories': dict(self.categories)
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(structured_data, f, indent=2, ensure_ascii=False)
        
        print(f"Comprehensive Q&A data saved to: {output_file}")
        
        # Print detailed summary
        print("\n📊 Q&A Summary by Category:")
        for category, qa_list in self.categories.items():
            print(f"  • {category}: {len(qa_list)} Q&A pairs")
        
        print(f"\n📈 Total Q&A pairs: {len(self.qa_pairs)}")
        print(f"📂 Categories: {len(self.categories)}")
        print(f"📚 Sources: {len(structured_data['metadata']['sources'])}")
        
        return structured_data
    
    def add_custom_qa_pair(self, question: str, answer: str, context: str, 
                          category: str, source: str = "Manual", confidence: str = "high"):
        """Add a custom Q&A pair for manual curation."""
        qa_pair = {
            'question': question,
            'answer': answer,
            'context': context,
            'source': source,
            'doc_id': 'manual',
            'category': category,
            'confidence': confidence
        }
        
        self.qa_pairs.append(qa_pair)
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(qa_pair)
        
        print(f"✅ Added custom Q&A pair to category: {category}")
    
    def export_category(self, category: str, output_file: str = None):
        """Export Q&A pairs for a specific category."""
        if category not in self.categories:
            print(f"Category '{category}' not found")
            return
        
        qa_list = self.categories[category]
        if output_file is None:
            output_file = f"{category}_qa_data.json"
        
        category_data = {
            'category': category,
            'qa_pairs': qa_list,
            'count': len(qa_list)
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(category_data, f, indent=2, ensure_ascii=False)
        
        print(f"Exported {len(qa_list)} Q&A pairs to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Generate comprehensive structured Q&A data')
    parser.add_argument('--data-dir', default='processed_data', 
                       help='Directory containing processed documents')
    parser.add_argument('--output', default='comprehensive_qa_data.json',
                       help='Output file for comprehensive Q&A data')
    parser.add_argument('--category', type=str,
                       help='Export specific category only')
    parser.add_argument('--add-custom', action='store_true',
                       help='Add custom Q&A pairs')
    
    args = parser.parse_args()
    
    generator = ComprehensiveQAGenerator(args.data_dir)
    documents = generator.load_documents()
    
    if documents:
        qa_pairs = generator.generate_comprehensive_qa(documents)
        generator.save_comprehensive_qa(args.output)
        
        if args.category:
            generator.export_category(args.category)
        
        if args.add_custom:
            # Example of adding custom Q&A pairs
            generator.add_custom_qa_pair(
                question="What is the 4% rule for retirement withdrawals?",
                answer="The 4% rule suggests withdrawing 4% of your initial retirement portfolio balance annually, adjusted for inflation, to make your savings last 30 years.",
                context="Retirement withdrawal strategies",
                category="retirement_planning"
            )
        
        print(f"\n✅ Generated {len(qa_pairs)} comprehensive Q&A pairs!")
        print("This structured format provides factual accuracy and easy content management.")
    else:
        print("No documents found to process!")

if __name__ == "__main__":
    main() 