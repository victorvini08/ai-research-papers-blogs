#!/usr/bin/env python3
"""
LLM-based paper summarization using Ollama/Groq API with Llama3
"""

import requests
import os
import json
import logging
from typing import Dict, List, Optional
from .paper import Paper

class LLMSummarizer:
    def __init__(self, model_name: str = "llama3", ollama_url: str = "http://localhost:11434"):
        """
        Initialize LLM summarizer with Ollama
        
        Args:
            model_name: Ollama model name (default: llama3)
            ollama_url: Ollama server URL (default: localhost:11434)
        """
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.logger = logging.getLogger(__name__)
        # Groq configuration
        self.groq_api_key = os.environ.get("GROQ_API_KEY")
        self.groq_model = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")
        
        # Test connection to Ollama
        try:
            self._test_connection()
        except Exception as e:
            self.logger.warning(f"Could not connect to Ollama at {ollama_url}: {e}")
            if self.groq_api_key:
                self.logger.warning("Falling back to Groq API for LLM generation")
            else:
                self.logger.warning("Falling back to rule-based summarization")
    
    def _test_connection(self):
        """Test connection to Ollama server"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            response.raise_for_status()
            self.logger.info(f"Connected to Ollama server at {self.ollama_url}")
        except Exception as e:
            raise Exception(f"Failed to connect to Ollama: {e}")
    
    def _generate_response(self, prompt: str) -> str:
        """Generate response using Ollama, fallback to Groq, then rule-based."""
        # Try Ollama first
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 500
                }
            }
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            generated_text = result.get('response', '').strip()
            if generated_text:
                return generated_text
        except Exception as e:
            self.logger.info(f"Ollama generation unavailable: {e}")

        # Fallback to Groq if API key is available
        if self.groq_api_key:
            try:
                headers = {
                    "Authorization": f"Bearer {self.groq_api_key}",
                    "Content-Type": "application/json"
                }
                groq_payload = {
                    "model": self.groq_model,
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant for summarizing research papers."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 800
                }
                groq_resp = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=groq_payload,
                    timeout=60
                )
                groq_resp.raise_for_status()
                groq_json = groq_resp.json()
                choices = groq_json.get("choices", [])
                if choices and choices[0].get("message", {}).get("content"):
                    return choices[0]["message"]["content"].strip()
            except Exception as e:
                self.logger.error(f"Groq API generation failed: {e}")

        # Last resort
        return self._rule_based_summary(prompt)
    
    def _rule_based_summary(self, prompt: str) -> str:
        """Fallback rule-based summarization when Ollama is not available"""
        # Extract key information using simple heuristics
        if "problem" in prompt.lower():
            return "This paper addresses challenges in data processing and analysis, focusing on improving efficiency and accuracy in computational tasks."
        elif "novelty" in prompt.lower():
            return "The paper introduces a new approach that combines multiple techniques to achieve better results than existing methods."
        elif "impact" in prompt.lower():
            return "This work has practical applications in real-world scenarios, potentially improving performance across various domains."
        else:
            return "This paper addresses important challenges in the field by introducing novel methodologies and approaches. The research contributes to advancing the state-of-the-art and has practical applications that could benefit various domains."
    
    def create_summarization_prompt(self, paper_sections: Dict[str, str], title: str) -> str:
        """Create an optimized prompt for paper summarization with structured sections"""
        # Extract key sections
        abstract = paper_sections.get('abstract', '')
        introduction = paper_sections.get('introduction', '')
        conclusion = paper_sections.get('conclusion', '')
        contributions = paper_sections.get('contributions', '')
        # Combine sections for analysis
        content = f"Title: {title}\n\n"
        if abstract:
            content += f"Abstract: {abstract}\n\n"
        if introduction:
            content += f"Introduction: {introduction}\n\n"
        if contributions:
            content += f"Contributions: {contributions}\n\n"
        if conclusion:
            content += f"Conclusion: {conclusion}\n\n"
        prompt = f"""
        You are an expert AI research communicator. Summarize the following research paper for a general audience, using clear Markdown section headings for each part. Use simple, engaging language.

        **Please structure your answer as follows:**

        ### Problem
        Describe the main problem or challenge the paper addresses.

        ### Key Innovation
        Explain what is new or unique about this work.

        ### Practical Impact
        Describe how this research could be applied in the real world, or why it matters.

        ### Analogy / Intuitive Explanation
        Explain the core idea using a simple analogy or metaphor, if possible.

        ---

        Here are the extracted sections from the paper:
        {content}

        ---

        **Write your summary below, using the section headings above. Don't write any Note in the beginning or end, just give the output in above 4 sections mentioned.**"""
        
        return prompt

    def parse_structured_summary(self, summary_text: str) -> dict:
        """Parse the LLM summary into sections based on Markdown headings or bold labels."""
        import re
        sections = {}
        current_section = None
        buffer = []
        # Acceptable section names (lowercase, for matching)
        section_names = [
            "problem", "problem", "main problem", "challenge",
            "key innovation", "innovation", "novelty", "contribution",
            "practical impact", "impact", "real-world impact", "implications",
            "analogy", "intuitive explanation", "analogy / intuitive explanation"
        ]
        # Regex for Markdown headings (### Section Name)
        heading_re = re.compile(r"^\s*#+\s*([A-Za-z0-9 /-]+)", re.IGNORECASE)
        # Regex for bold label (e.g., **Problem:**)
        bold_label_re = re.compile(r"^\s*\*\*([A-Za-z0-9 /-]+):?\*\*", re.IGNORECASE)
        lines = summary_text.splitlines()
        for line in lines:
            heading_match = heading_re.match(line)
            bold_match = bold_label_re.match(line)
            section = None
            if heading_match:
                section = heading_match.group(1).strip().lower()
            elif bold_match:
                section = bold_match.group(1).strip().lower()
            # Normalize section name
            if section:
                for name in section_names:
                    if name in section:
                        if current_section and buffer:
                            sections[current_section] = "\n".join(buffer).strip()
                        current_section = name
                        buffer = []
                        break
                continue
            if current_section:
                buffer.append(line)
        if current_section and buffer:
            sections[current_section] = "\n".join(buffer).strip()
        return sections if sections else {"summary": summary_text.strip()}

    def summarize_paper(self, paper_sections: Dict[str, str], paper: Paper) -> dict:
        """
        Summarize a paper using LLM and return structured sections if possible
        """
        try:
            prompt = self.create_summarization_prompt(paper_sections, paper.title)
            summary = self._generate_response(prompt)
            parsed = self.parse_structured_summary(summary)
            return parsed
        except Exception as e:
            self.logger.error(f"Error summarizing paper {paper.arxiv_id}: {e}")
            return {"summary": self._rule_based_summary("")}
    
    def batch_summarize_papers(self, papers_with_sections: List[tuple]) -> List[str]:
        """
        Summarize multiple papers in batch
        
        Args:
            papers_with_sections: List of tuples (paper_sections, paper)
        
        Returns:
            List of summary strings
        """
        summaries = []
        
        for paper_sections, paper in papers_with_sections:
            try:
                summary = self.summarize_paper(paper_sections, paper)
                summaries.append(summary)
            except Exception as e:
                self.logger.error(f"Error summarizing paper {paper.arxiv_id}: {e}")
                summaries.append(self._rule_based_summary(""))
        
        return summaries
    
   
