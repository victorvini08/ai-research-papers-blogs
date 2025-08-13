#!/usr/bin/env python3
"""
Setup script for Ollama and Llama3 model
"""

import subprocess
import requests
import json
import sys

def check_ollama_installation():
    """Check if Ollama is installed and running"""
    try:
        # Check if ollama command exists
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ollama is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Ollama is not installed or not in PATH")
            return False
    except FileNotFoundError:
        print("❌ Ollama is not installed. Please install it from https://ollama.ai")
        return False

def check_ollama_server():
    """Check if Ollama server is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama server is running")
            return True
        else:
            print("❌ Ollama server is not responding")
            return False
    except requests.exceptions.RequestException:
        print("❌ Ollama server is not running. Please start it with: ollama serve")
        return False

def check_llama3_model():
    """Check if Llama3 model is available"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            for model in models:
                if 'llama3' in model.get('name', '').lower():
                    print(f"✅ Llama3 model found: {model['name']}")
                    return True
            print("❌ Llama3 model not found")
            return False
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        return False

def install_llama3():
    """Install Llama3 model"""
    print("📥 Installing Llama3 model...")
    try:
        result = subprocess.run(['ollama', 'pull', 'llama3'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Llama3 model installed successfully")
            return True
        else:
            print(f"❌ Failed to install Llama3: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing Llama3: {e}")
        return False

def main():
    """Main setup function"""
    print("🔧 Setting up Ollama for AI Research Papers Summarizer")
    print("=" * 60)
    
    # Check Ollama installation
    if not check_ollama_installation():
        print("\n📋 Installation instructions:")
        print("1. Visit https://ollama.ai")
        print("2. Download and install Ollama for your platform")
        print("3. Run this script again")
        return False
    
    # Check Ollama server
    if not check_ollama_server():
        print("\n📋 To start Ollama server:")
        print("1. Open a terminal")
        print("2. Run: ollama serve")
        print("3. Keep the terminal open")
        print("4. Run this script again in another terminal")
        return False
    
    # Check Llama3 model
    if not check_llama3_model():
        print("\n📥 Llama3 model not found. Installing...")
        if not install_llama3():
            print("\n❌ Failed to install Llama3 model")
            return False
    
    print("\n✅ Setup complete! You can now run the AI Research Papers Summarizer")
    print("📝 To test the setup, run: python3 test_llm_summarization.py")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
