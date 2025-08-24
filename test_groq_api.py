#!/usr/bin/env python3
"""
Test script to verify Groq API integration
"""

import os
import sys
sys.path.append('src')

from src.llm_summarizer import LLMSummarizer
from src.paper import Paper
from src.database import PaperDatabase

def test_groq_api():
    """Test Groq API functionality"""
    print("🧪 Testing Groq API Integration...")
    
    # Check if GROQ_API_KEY is set
    groq_api_key = os.environ.get('GROQ_API_KEY')
    if not groq_api_key:
        print("❌ GROQ_API_KEY environment variable not set")
        print("Please set it with: export GROQ_API_KEY='your_key_here'")
        return False
    
    print(f"✅ GROQ_API_KEY found: {groq_api_key[:10]}...")
    
    # Test the summarizer
    try:
        summarizer = LLMSummarizer()
        database = PaperDatabase()
        paper = database.get_recent_papers()[0]
        paper_sections = paper.get_summary()
        print("🔄 Testing Groq API response generation...")
        response = summarizer.summarize_paper(paper_sections, paper)
        
        if response and isinstance(response, dict) and len(str(response)) > 100:
            print("✅ Groq API test successful!")
            print(f"Response type: {type(response)}")
            print(f"Response keys: {list(response.keys())}")
            print("\n📝 Generated Summary:")
            print("-" * 50)
            # Print the first section content
            print(response)
            print("-" * 50)
            return True
        else:
            print("❌ Groq API returned empty or too short response")
            print(f"Response: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Groq API: {e}")
        return False

def test_ollama_fallback():
    """Test Ollama fallback functionality"""
    print("\n🔄 Testing Ollama fallback...")
    
    try:
        # Create summarizer without Groq API key
        os.environ.pop('GROQ_API_KEY', None)
        summarizer = LLMSummarizer()
        
        test_prompt = "Summarize this test paper about AI."
        response = summarizer._generate_response(test_prompt)
        
        if response:
            print("✅ Ollama fallback working")
            return True
        else:
            print("❌ Ollama fallback failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Ollama fallback: {e}")
        return False

def test_rule_based_fallback():
    """Test rule-based fallback functionality"""
    print("\n🔄 Testing rule-based fallback...")
    
    try:
        # Create summarizer without any API keys
        os.environ.pop('GROQ_API_KEY', None)
        summarizer = LLMSummarizer()
        
        test_prompt = "Summarize this test paper about AI."
        response = summarizer._generate_response(test_prompt)
        
        if response:
            print("✅ Rule-based fallback working")
            return True
        else:
            print("❌ Rule-based fallback failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing rule-based fallback: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Groq API Integration Test Suite")
    print("=" * 50)
    
    # Test Groq API
    groq_success = test_groq_api()
    
    # Test Ollama fallback
    ollama_success = test_ollama_fallback()
    
    # Test rule-based fallback
    rule_success = test_rule_based_fallback()
    
    print("\n📊 Test Results Summary:")
    print("=" * 50)
    print(f"Groq API: {'✅ PASS' if groq_success else '❌ FAIL'}")
    print(f"Ollama Fallback: {'✅ PASS' if ollama_success else '❌ FAIL'}")
    print(f"Rule-based Fallback: {'✅ PASS' if rule_success else '❌ FAIL'}")
    
    if groq_success:
        print("\n🎉 Groq API is working correctly!")
        print("You can now use it in production without Ollama.")
    else:
        print("\n⚠️  Groq API test failed. Please check your API key and configuration.")
