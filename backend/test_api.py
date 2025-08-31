#!/usr/bin/env python3
"""
Simple test script for LegalSense AI API
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_upload_sample():
    """Test document upload with sample text"""
    try:
        # Create a sample text file
        sample_text = """
        EMPLOYMENT AGREEMENT
        
        This Employment Agreement (the "Agreement") is entered into on January 1, 2024, 
        between ABC Company ("Employer") and John Doe ("Employee").
        
        TERMS OF EMPLOYMENT:
        1. Position: Software Engineer
        2. Salary: $80,000 per year
        3. Effective Date: January 1, 2024
        4. Termination Date: December 31, 2024
        
        OBLIGATIONS:
        - Employee shall perform duties as assigned
        - Employee must maintain confidentiality
        - Employer shall provide necessary tools and equipment
        
        TERMINATION:
        This agreement may be terminated by either party with 30 days written notice.
        """
        
        # Create a temporary file
        with open("test_sample.txt", "w") as f:
            f.write(sample_text)
        
        # Upload the file
        with open("test_sample.txt", "rb") as f:
            files = {"file": ("test_sample.txt", f, "text/plain")}
            data = {"language": "en"}
            response = requests.post(f"{BASE_URL}/api/upload", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload test passed")
            print(f"   Document ID: {result['document_id']}")
            return result['document_id']
        else:
            print(f"❌ Upload test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Upload test error: {e}")
        return None

def test_analysis(document_id):
    """Test document analysis"""
    try:
        data = {
            "document_id": document_id,
            "language": "en"
        }
        response = requests.post(f"{BASE_URL}/api/analyze", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Analysis test passed")
            print(f"   Document title: {result['analysis']['doc']['title']}")
            print(f"   Parties found: {len(result['analysis']['doc']['parties'])}")
            print(f"   Clauses found: {len(result['analysis']['doc']['clauses'])}")
            return True
        else:
            print(f"❌ Analysis test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Analysis test error: {e}")
        return False

def test_qa(document_id):
    """Test question answering"""
    try:
        data = {
            "document_id": document_id,
            "question": "Who are the parties in this agreement?",
            "language": "en"
        }
        response = requests.post(f"{BASE_URL}/api/qa", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Q&A test passed")
            print(f"   Answer: {result['answer'][:100]}...")
            return True
        else:
            print(f"❌ Q&A test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Q&A test error: {e}")
        return False

def cleanup():
    """Clean up test files"""
    try:
        import os
        if os.path.exists("test_sample.txt"):
            os.remove("test_sample.txt")
        print("✅ Cleanup completed")
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")

def main():
    """Run all tests"""
    print("🧪 LegalSense AI API Test Suite")
    print("=" * 40)
    
    # Wait for server to start
    print("⏳ Waiting for server to be ready...")
    time.sleep(5)
    
    # Test health
    if not test_health():
        print("❌ Server is not ready. Please start the backend first.")
        return
    
    # Test upload
    document_id = test_upload_sample()
    if not document_id:
        print("❌ Upload test failed. Stopping tests.")
        return
    
    # Test analysis
    if not test_analysis(document_id):
        print("❌ Analysis test failed.")
        return
    
    # Test Q&A
    if not test_qa(document_id):
        print("❌ Q&A test failed.")
        return
    
    # Cleanup
    cleanup()
    
    print("\n🎉 All tests passed! The API is working correctly.")
    print("\n📱 You can now use the frontend at http://localhost:3000")

if __name__ == "__main__":
    main()
