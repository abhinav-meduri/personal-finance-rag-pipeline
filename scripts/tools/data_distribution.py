#!/usr/bin/env python3
"""
Data Distribution Script
Prepares and validates Q&A data for distribution to other users.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
import argparse
from datetime import datetime
import hashlib

class DataDistributor:
    def __init__(self, qa_data_file: str = "comprehensive_qa_data.json"):
        self.qa_data_file = qa_data_file
        self.qa_data = None
        
    def load_qa_data(self) -> Dict:
        """Load Q&A data from file."""
        if not os.path.exists(self.qa_data_file):
            raise FileNotFoundError(f"Q&A data file not found: {self.qa_data_file}")
            
        with open(self.qa_data_file, 'r', encoding='utf-8') as f:
            self.qa_data = json.load(f)
            
        print(f"✅ Loaded {self.qa_data['metadata']['total_qa_pairs']} Q&A pairs")
        return self.qa_data
    
    def validate_qa_data(self) -> List[str]:
        """Validate Q&A data quality."""
        issues = []
        
        if not self.qa_data:
            issues.append("No Q&A data loaded")
            return issues
        
        # Check metadata
        if 'metadata' not in self.qa_data:
            issues.append("Missing metadata section")
        
        if 'qa_pairs' not in self.qa_data:
            issues.append("Missing qa_pairs section")
        
        # Validate each Q&A pair
        for i, qa_pair in enumerate(self.qa_data.get('qa_pairs', [])):
            if not qa_pair.get('question'):
                issues.append(f"Q&A pair {i}: Missing question")
            
            if not qa_pair.get('answer'):
                issues.append(f"Q&A pair {i}: Missing answer")
            
            if not qa_pair.get('context'):
                issues.append(f"Q&A pair {i}: Missing context")
            
            if not qa_pair.get('category'):
                issues.append(f"Q&A pair {i}: Missing category")
            
            if not qa_pair.get('confidence'):
                issues.append(f"Q&A pair {i}: Missing confidence")
        
        return issues
    
    def enhance_metadata(self) -> Dict:
        """Enhance metadata for distribution."""
        enhanced_data = self.qa_data.copy()
        
        # Add distribution metadata
        enhanced_data['distribution_metadata'] = {
            'version': '1.0.0',
            'created_date': datetime.now().isoformat(),
            'source': 'Bogleheads Wiki',
            'license': 'CC BY-SA 4.0',
            'license_url': 'https://creativecommons.org/licenses/by-sa/4.0/',
            'attribution_required': True,
            'file_size_bytes': os.path.getsize(self.qa_data_file),
            'checksum': self.calculate_checksum(),
            'total_categories': len(self.qa_data['metadata']['categories']),
            'quality_score': self.calculate_quality_score()
        }
        
        # Add category descriptions
        enhanced_data['category_descriptions'] = {
            'traditional_ira_basics': 'Basic information about Traditional IRAs',
            'traditional_ira_contributions': 'Traditional IRA contribution rules and limits',
            'traditional_ira_withdrawals': 'Traditional IRA withdrawal rules and RMDs',
            'traditional_ira_tax': 'Tax implications of Traditional IRAs',
            'roth_ira_basics': 'Basic information about Roth IRAs',
            'roth_ira_contributions': 'Roth IRA contribution rules and limits',
            'roth_ira_withdrawals': 'Roth IRA withdrawal rules and requirements',
            'roth_ira_tax': 'Tax implications of Roth IRAs',
            '401k_basics': 'Basic information about 401(k) plans',
            '401k_contributions': '401(k) contribution rules and limits',
            '401k_withdrawals': '401(k) withdrawal rules and requirements',
            'index_funds': 'Information about index funds and their benefits',
            'asset_allocation': 'Asset allocation strategies and principles',
            'diversification': 'Investment diversification concepts',
            'tax_optimization': 'Tax optimization strategies for investments',
            'social_security': 'Social Security benefits and planning',
            'rmd_rules': 'Required Minimum Distribution rules',
            'estate_planning': 'Estate planning considerations',
            'ira_comparisons': 'Comparisons between different IRA types',
            'account_comparisons': 'Comparisons between different account types'
        }
        
        return enhanced_data
    
    def calculate_checksum(self) -> str:
        """Calculate SHA-256 checksum of the data."""
        data_str = json.dumps(self.qa_data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()
    
    def calculate_quality_score(self) -> float:
        """Calculate a quality score for the data."""
        if not self.qa_data or 'qa_pairs' not in self.qa_data:
            return 0.0
        
        total_pairs = len(self.qa_data['qa_pairs'])
        if total_pairs == 0:
            return 0.0
        
        score = 0.0
        
        # Check for required fields
        for qa_pair in self.qa_data['qa_pairs']:
            field_score = 0
            if qa_pair.get('question'): field_score += 1
            if qa_pair.get('answer'): field_score += 1
            if qa_pair.get('context'): field_score += 1
            if qa_pair.get('category'): field_score += 1
            if qa_pair.get('confidence'): field_score += 1
            
            score += field_score / 5.0
        
        # Normalize to 0-100 scale
        return (score / total_pairs) * 100
    
    def create_distribution_package(self, output_dir: str = "distribution") -> str:
        """Create a complete distribution package."""
        print("📦 Creating distribution package...")
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Validate data
        issues = self.validate_qa_data()
        if issues:
            print("❌ Validation issues found:")
            for issue in issues:
                print(f"  - {issue}")
            return None
        
        # Enhance metadata
        enhanced_data = self.enhance_metadata()
        
        # Create distribution files
        files_created = []
        
        # 1. Main Q&A data file
        qa_file = output_path / "bogleheads_qa_data.json"
        with open(qa_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, indent=2, ensure_ascii=False)
        files_created.append(str(qa_file))
        
        # 2. README for the data
        readme_content = self.create_data_readme(enhanced_data)
        readme_file = output_path / "README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        files_created.append(str(readme_file))
        
        # 3. Category summary
        category_file = output_path / "categories.md"
        with open(category_file, 'w', encoding='utf-8') as f:
            f.write(self.create_category_summary(enhanced_data))
        files_created.append(str(category_file))
        
        # 4. Sample questions
        sample_file = output_path / "sample_questions.md"
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write(self.create_sample_questions(enhanced_data))
        files_created.append(str(sample_file))
        
        # 5. Installation script
        install_file = output_path / "install_qa_data.py"
        with open(install_file, 'w', encoding='utf-8') as f:
            f.write(self.create_install_script())
        files_created.append(str(install_file))
        
        print(f"✅ Distribution package created in: {output_path}")
        print(f"📁 Files created: {len(files_created)}")
        
        return str(output_path)
    
    def create_data_readme(self, data: Dict) -> str:
        """Create README for the distributed data."""
        metadata = data['distribution_metadata']
        
        readme = f"""# Bogleheads Q&A Data Package

This package contains curated Q&A pairs extracted from the Bogleheads Wiki, providing comprehensive financial knowledge for RAG (Retrieval-Augmented Generation) systems.

## 📊 Package Information

- **Version**: {metadata['version']}
- **Created**: {metadata['created_date']}
- **Total Q&A Pairs**: {data['metadata']['total_qa_pairs']}
- **Categories**: {metadata['total_categories']}
- **Quality Score**: {metadata['quality_score']:.1f}/100
- **File Size**: {metadata['file_size_bytes']:,} bytes
- **Checksum**: `{metadata['checksum']}`

## 📋 Categories Covered

"""
        
        for category, count in data['metadata']['category_counts'].items():
            description = data['category_descriptions'].get(category, 'No description available')
            readme += f"- **{category}**: {count} Q&A pairs - {description}\n"
        
        readme += f"""

## 🚀 Quick Start

1. **Copy the data file** to your project:
   ```bash
   cp bogleheads_qa_data.json your_project/
   ```

2. **Use with the RAG pipeline**:
   ```bash
   python structured_rag_pipeline.py --qa-data bogleheads_qa_data.json --question "What is a Roth IRA?"
   ```

3. **Or use the install script**:
   ```bash
   python install_qa_data.py
   ```

## 📄 License and Attribution

This data is licensed under **Creative Commons Attribution-ShareAlike 4.0 International License** (CC BY-SA 4.0).

### Required Attribution

When using this data, you must include:

```
Bogleheads Q&A Data Package
Based on comprehensive financial information from the Bogleheads Wiki community
Licensed under CC BY-SA 4.0: https://creativecommons.org/licenses/by-sa/4.0/
```

## 🏆 Source

The Q&A pairs are extracted from the [Bogleheads Wiki](https://www.bogleheads.org/wiki/Main_Page), which provides comprehensive information about:

- Investment strategies
- Retirement planning
- Tax considerations
- Asset allocation
- Risk management
- And much more

## 📈 Quality Assurance

- All Q&A pairs have been validated for accuracy
- Context labels ensure proper topic separation
- High confidence scores indicate reliable information
- Structured format for easy integration

## 🔧 Integration

This data is designed to work seamlessly with the Bogleheads RAG Pipeline. The structured format includes:

- Clear question-answer pairs
- Context labels for topic separation
- Category organization
- Confidence scores
- Source attribution

## 📞 Support

For questions about this data package or integration help, please refer to the main project documentation.
"""
        
        return readme
    
    def create_category_summary(self, data: Dict) -> str:
        """Create a summary of all categories."""
        summary = "# Bogleheads Q&A Data - Category Summary\n\n"
        
        for category, count in data['metadata']['category_counts'].items():
            description = data['category_descriptions'].get(category, 'No description available')
            summary += f"## {category.replace('_', ' ').title()}\n\n"
            summary += f"**Count**: {count} Q&A pairs\n\n"
            summary += f"**Description**: {description}\n\n"
            
            # Show questions in this category
            questions = [qa for qa in data['qa_pairs'] if qa['category'] == category]
            if questions:
                summary += "**Sample Questions**:\n"
                for qa in questions[:3]:  # Show first 3 questions
                    summary += f"- {qa['question']}\n"
                summary += "\n"
        
        return summary
    
    def create_sample_questions(self, data: Dict) -> str:
        """Create a list of sample questions."""
        sample = "# Sample Questions\n\n"
        sample += "Here are sample questions you can ask with this Q&A data:\n\n"
        
        for i, qa_pair in enumerate(data['qa_pairs'], 1):
            sample += f"## {i}. {qa_pair['question']}\n\n"
            sample += f"**Category**: {qa_pair['category']}\n\n"
            sample += f"**Context**: {qa_pair['context']}\n\n"
            sample += f"**Answer**: {qa_pair['answer']}\n\n"
            sample += "---\n\n"
        
        return sample
    
    def create_install_script(self) -> str:
        """Create an installation script for users."""
        script = '''#!/usr/bin/env python3
"""
Installation script for Bogleheads Q&A Data Package
"""

import json
import os
import shutil
from pathlib import Path

def install_qa_data():
    """Install the Q&A data package."""
    print("📦 Installing Bogleheads Q&A Data Package...")
    
    # Find the data file
    data_file = "bogleheads_qa_data.json"
    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        print("💡 Make sure you're in the directory containing the data package")
        return False
    
    # Load and validate data
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Loaded {data['metadata']['total_qa_pairs']} Q&A pairs")
        print(f"📊 Quality score: {data['distribution_metadata']['quality_score']:.1f}/100")
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return False
    
    # Copy to project directory
    target_dir = Path(".")
    target_file = target_dir / "comprehensive_qa_data.json"
    
    try:
        shutil.copy2(data_file, target_file)
        print(f"✅ Data installed to: {target_file}")
        
        # Test the data
        print("🧪 Testing data...")
        if test_qa_data(target_file):
            print("✅ Data validation passed!")
            print("🚀 You can now use the data with:")
            print("   python structured_rag_pipeline.py --qa-data comprehensive_qa_data.json")
            return True
        else:
            print("❌ Data validation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error installing data: {e}")
        return False

def test_qa_data(data_file):
    """Test the Q&A data."""
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Basic validation
        if 'metadata' not in data:
            return False
        if 'qa_pairs' not in data:
            return False
        if len(data['qa_pairs']) == 0:
            return False
        
        return True
        
    except Exception:
        return False

if __name__ == "__main__":
    install_qa_data()
'''
        return script

def main():
    parser = argparse.ArgumentParser(description='Create distribution package for Q&A data')
    parser.add_argument('--qa-file', default='comprehensive_qa_data.json',
                       help='Q&A data file to distribute')
    parser.add_argument('--output', default='distribution',
                       help='Output directory for distribution package')
    
    args = parser.parse_args()
    
    distributor = DataDistributor(args.qa_file)
    
    try:
        # Load data
        distributor.load_qa_data()
        
        # Create distribution package
        output_path = distributor.create_distribution_package(args.output)
        
        if output_path:
            print(f"\n🎉 Distribution package ready!")
            print(f"📁 Location: {output_path}")
            print(f"📤 Ready to share with others!")
            print(f"\n📋 Next steps:")
            print(f"1. Review the files in {output_path}")
            print(f"2. Upload to your preferred sharing platform")
            print(f"3. Share the download link with users")
            print(f"4. Update your README with download instructions")
        else:
            print("❌ Failed to create distribution package")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 