#!/usr/bin/env python3
"""
Test script for LLM-based paper summarization
"""

import json
from src.arxiv_paper_fetcher import PaperFetcher
from src.llm_summarizer import LLMSummarizer
from src.paper import Paper

def test_llm_summarization():
    """Test the LLM summarization functionality"""
    
    print("🧪 Testing LLM Summarization with Ollama")
    print("=" * 50)
    
    # Initialize components
    fetcher = PaperFetcher()
    print("Connecting to Ollama server...")
    llm_summarizer = LLMSummarizer()
    print("Connected to Ollama successfully")
    
    # Test with a sample paper
    test_paper = Paper(
        '2507.23676v1', 
        'DepMicroDiff: Diffusion-Based Dependency-Aware Multimodal Imputation for Microbiome Data', 
        ['Rabeya Tus Sadia', 'Qiang Cheng'],
        'Test abstract', 
        ['cs.AI'], 
        '2024-01-01',
        'https://arxiv.org/pdf/2507.23676v1', 
        'https://arxiv.org/abs/2507.23676v1'
    )
    
    try:
        print("1. Extracting paper sections...")
        paper_sections = test_paper.get_summary()
        
        if 'error' in paper_sections:
            print(f"❌ Error extracting sections: {paper_sections['error']}")
            return False
        
        print(f"✅ Extracted sections: {list(paper_sections.keys())}")
        
        print("\n2. Generating LLM summary...")
        llm_summary = llm_summarizer.summarize_paper(paper_sections, test_paper)
        
        print("✅ LLM Summary generated:")
        print("LLM Summary: ", llm_summary)
        
        # Save results
        results = {
            'paper_title': test_paper.title,
            'paper_sections': paper_sections,
            'llm_summary': llm_summary
        }
        
        with open('llm_summarization_test.json', 'w') as f:
            json.dump(results, f, indent=4)
        
        print("\n✅ Results saved to llm_summarization_test.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_llm_summarization() 