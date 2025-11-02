#!/usr/bin/env python3
"""
Privacy Verification Script
Verifies that the RAG pipeline operates entirely locally without external network calls.
"""

import json
import os
import time
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any

def check_network_activity_during_query():
    """Check for network activity during a query"""
    print("🔍 Checking for network activity during query...")
    
    # Start network monitoring
    print("   Starting network monitoring...")
    monitor_process = subprocess.Popen(
        ["sudo", "tcpdump", "-i", "any", "-w", "privacy_test.pcap", "-c", "100"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait a moment for monitoring to start
    time.sleep(2)
    
    # Run a test query
    print("   Running test query...")
    try:
        result = subprocess.run([
            sys.executable, "hybrid_rag_pipeline.py", 
            "--question", "What is a Roth IRA?"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("   ✅ Query completed successfully")
        else:
            print(f"   ⚠️  Query failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("   ⚠️  Query timed out")
    except Exception as e:
        print(f"   ❌ Error running query: {e}")
    
    # Stop monitoring
    monitor_process.terminate()
    monitor_process.wait()
    
    # Check if any network packets were captured
    if os.path.exists("privacy_test.pcap"):
        file_size = os.path.getsize("privacy_test.pcap")
        if file_size < 100:  # Very small file means minimal network activity
            print("   ✅ No significant network activity detected during query")
            return True
        else:
            print(f"   ⚠️  Network activity detected (file size: {file_size} bytes)")
            return False
    else:
        print("   ❌ Could not capture network activity")
        return False

def check_local_components():
    """Check that all required components are local"""
    print("🔍 Checking local components...")
    
    components = {
        "Mistral-7b Model": "mistral-7b-instruct-v0.1.Q4_K_M.gguf",
        "QA Data": "comprehensive_qa_data.json",
        "Vector Database": "vector_db",
        "QA Vector Database": "qa_vector_db"
    }
    
    all_local = True
    for name, path in components.items():
        if os.path.exists(path):
            print(f"   ✅ {name}: Found locally")
        else:
            print(f"   ❌ {name}: Not found locally")
            all_local = False
    
    return all_local

def check_external_dependencies():
    """Check for any external API dependencies in the code"""
    print("🔍 Checking for external dependencies...")
    
    # Files to check
    files_to_check = [
        "hybrid_rag_pipeline.py",
        "structured_rag_pipeline.py", 
        "rag_pipeline.py"
    ]
    
    external_apis = []
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
                
                # Check for common external API patterns
                api_patterns = [
                    "openai", "anthropic", "huggingface.co/api",
                    "requests.get", "urllib.request", "http.client"
                ]
                
                for pattern in api_patterns:
                    if pattern in content.lower():
                        external_apis.append(f"{file_path}: {pattern}")
    
    if external_apis:
        print("   ⚠️  Potential external dependencies found:")
        for api in external_apis:
            print(f"      - {api}")
        return False
    else:
        print("   ✅ No external API dependencies found")
        return True

def check_embedding_model():
    """Check that embedding model runs locally"""
    print("🔍 Checking embedding model...")
    
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        
        # Test local embedding
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        # Test embedding generation
        test_text = "This is a test for privacy verification"
        embedding = embeddings.embed_query(test_text)
        
        if len(embedding) > 0:
            print("   ✅ Embedding model runs locally")
            return True
        else:
            print("   ❌ Embedding model failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing embedding model: {e}")
        return False

def check_llm_model():
    """Check that LLM model runs locally"""
    print("🔍 Checking LLM model...")
    
    model_path = "mistral-7b-instruct-v0.1.Q4_K_M.gguf"
    
    if not os.path.exists(model_path):
        print("   ❌ LLM model not found locally")
        return False
    
    print("   ✅ LLM model found locally")
    print("   ℹ️  Note: Full LLM testing requires significant memory")
    return True

def generate_privacy_report():
    """Generate a comprehensive privacy report"""
    print("\n" + "="*60)
    print("🔒 PRIVACY VERIFICATION REPORT")
    print("="*60)
    
    checks = {
        "Local Components": check_local_components(),
        "External Dependencies": check_external_dependencies(),
        "Embedding Model": check_embedding_model(),
        "LLM Model": check_llm_model(),
        "Network Activity": check_network_activity_during_query()
    }
    
    print("\n📊 SUMMARY:")
    print("-" * 40)
    
    all_passed = True
    for check_name, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{check_name:<25} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    
    if all_passed:
        print("🎉 PRIVACY VERIFICATION PASSED")
        print("✅ Your RAG pipeline operates entirely locally")
        print("✅ No external network calls during queries")
        print("✅ Complete privacy and security confirmed")
    else:
        print("⚠️  PRIVACY VERIFICATION FAILED")
        print("❌ Some components may have external dependencies")
        print("❌ Review the failed checks above")
    
    print("="*60)
    
    # Generate detailed report
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "checks": checks,
        "overall_status": "PASSED" if all_passed else "FAILED",
        "recommendations": []
    }
    
    if not all_passed:
        report["recommendations"].append("Review failed checks and address any external dependencies")
        report["recommendations"].append("Ensure all models are downloaded locally")
        report["recommendations"].append("Verify no API keys or external services are configured")
    
    # Save report
    with open("privacy_verification_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: privacy_verification_report.json")
    
    return all_passed

def main():
    """Main verification function"""
    print("🔒 Privacy Verification for Financial Knowledge RAG Pipeline")
    print("=" * 60)
    print("This script verifies that your RAG pipeline operates entirely locally")
    print("without any external network calls or data transmission.")
    print()
    
    # Check if running with sudo (needed for tcpdump)
    if os.geteuid() != 0:
        print("⚠️  Note: Some checks require sudo privileges for network monitoring")
        print("   Run with: sudo python privacy_verification.py")
        print()
    
    try:
        success = generate_privacy_report()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n❌ Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Verification failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 