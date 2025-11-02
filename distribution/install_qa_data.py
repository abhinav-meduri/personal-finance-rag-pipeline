#!/usr/bin/env python3
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
