#!/usr/bin/env python3
"""
Simple test script to verify the AI Research Papers Daily application
"""

import requests
import time
import json

def test_app():
    """Test the web application endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing AI Research Papers Daily Application")
    print("=" * 50)
    
    # Test 1: Home page
    print("\n1. Testing home page...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("✅ Home page is accessible")
        else:
            print(f"❌ Home page returned status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing home page: {e}")
    
    # Test 2: Archive page
    print("\n2. Testing archive page...")
    try:
        response = requests.get(f"{base_url}/archive", timeout=10)
        if response.status_code == 200:
            print("✅ Archive page is accessible")
        else:
            print(f"❌ Archive page returned status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing archive page: {e}")
    
    # Test 3: API endpoint (without fetching papers)
    print("\n3. Testing API endpoints...")
    try:
        # Test generate summary endpoint
        response = requests.post(
            f"{base_url}/api/generate-summary",
            json={"date": "2024-01-01"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code in [200, 404]:  # 404 is expected if no papers for that date
            print("✅ Generate summary API is working")
        else:
            print(f"❌ Generate summary API returned status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing API: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Application test completed!")
    print(f"🌐 Open your browser and go to: {base_url}")
    print("📝 You can now:")
    print("   - View the home page")
    print("   - Browse the archive")
    print("   - Click 'Fetch Papers' to get latest AI research papers")
    print("   - Generate daily summaries")

if __name__ == "__main__":
    test_app() 