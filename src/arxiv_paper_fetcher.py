import arxiv
import requests
import os
import feedparser
import tempfile
import pymupdf
from datetime import datetime, timedelta
from typing import List, Dict
import time
import re
from .paper import Paper

class PaperFetcher:
    def __init__(self):
        self.categories = [
            'cs.AI', 'cs.LG', 'cs.CL', 'cs.CV', 'cs.NE', 'cs.RO',
            'stat.ML', 'cs.SE'
        ]
        self.client = arxiv.Client(
            page_size=100,
            delay_seconds=3,
            num_retries=3
        )
    
    def fetch_recent_papers(self, max_results: int = 50) -> List[Paper]:
        """Fetch recent papers from arXiv"""
        papers = []
        
        # Search for recent papers in AI/ML categories
        search_query = " OR ".join([f"cat:{cat}" for cat in self.categories])
        search = arxiv.Search(
            query=search_query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        try:
            for result in self.client.results(search):
                paper = Paper( 
                    arxiv_id=result.entry_id.split('/')[-1],
                    title=result.title,
                    authors=[author.name for author in result.authors],
                    abstract=result.summary,
                    categories=result.categories,
                    published_data=result.published.strftime('%Y-%m-%d'),
                    pdf_url=result.pdf_url,
                    entry_id=result.entry_id
                )
                papers.append(paper)
                
                # Add delay to be respectful to arXiv servers
                time.sleep(1)
                
        except Exception as e:
            print(f"Error fetching papers: {e}")
        
        return papers
    
    def fetch_papers_by_date(self, date: str) -> List[Paper]:
        """Fetch papers published on a specific date"""
        papers = []
        
        # Convert date string to datetime
        target_date = datetime.strptime(date, '%Y-%m-%d')
        
        # Search for papers in the last few days to ensure we catch the target date
        search_query = " OR ".join([f"cat:{cat}" for cat in self.categories])
        search = arxiv.Search(
            query=search_query,
            max_results=20,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        try:
            for result in self.client.results(search):
                paper_date = result.published.date()
                
                if paper_date == target_date.date():
                    paper = Paper( 
                    arxiv_id=result.entry_id.split('/')[-1],
                    title=result.title,
                    authors=[author.name for author in result.authors],
                    abstract=result.summary,
                    categories=result.categories,
                    published_data=result.published.strftime('%Y-%m-%d'),
                    pdf_url=result.pdf_url,
                    entry_id=result.entry_id
                )
                    papers.append(paper)
                
                # Stop if we've gone past our target date
                if paper_date < target_date.date():
                    break
                    
                time.sleep(1)
                
        except Exception as e:
            print(f"Error fetching papers for date {date}: {e}")
        
        return papers
    
    def filter_relevant_papers(self, papers: List[Paper]) -> List[Paper]:
        """Filter papers to keep only the most relevant ones"""
        relevant_papers = []
        
        # Keywords that indicate high relevance
        relevant_keywords = [
            'large language model', 'llm', 'transformer', 'attention',
            'neural network', 'deep learning', 'machine learning',
            'artificial intelligence', 'ai', 'natural language',
            'computer vision', 'reinforcement learning', 'generative',
            'foundation model', 'multimodal', 'diffusion', 'gan',
            'bert', 'gpt', 'claude', 'llama', 'chatgpt'
        ]
        
        for paper in papers:
            title_lower = paper.title.lower()
            abstract_lower = paper.abstract.lower()
            
            # Check if paper contains relevant keywords
            relevance_score = 0
            for keyword in relevant_keywords:
                if keyword in title_lower or keyword in abstract_lower:
                    relevance_score += 1
            
            # Keep papers with at least one relevant keyword
            if relevance_score > 0:
                paper.relevance_score = relevance_score
                relevant_papers.append(paper)
        
        # Sort by relevance score
        relevant_papers.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return relevant_papers[:30]  # Limit to top 30 most relevant papers
    
    def get_paper_metadata(self, arxiv_id: str) -> Paper:
        """Get detailed metadata for a specific paper"""
        try:
            search = arxiv.Search(id_list=[arxiv_id])
            result = next(self.client.results(search))
            
            return Paper(
                arxiv_id=result.entry_id.split('/')[-1],
                title=result.title,
                authors=[author.name for author in result.authors],
                abstract=result.summary,
                categories=result.categories,
                published_data=result.published.strftime('%Y-%m-%d'),
                pdf_url=result.pdf_url,
                entry_id=result.entry_id
            )
        except Exception as e:
            print(f"Error fetching metadata for {arxiv_id}: {e}")
            return None
        
    
    def fetch_papers_by_category(self, keywords: list, max_results: int = 3) -> List[Paper]:
        """
        Fetch papers from arXiv matching any of the provided keywords in title or abstract.
        """
        papers = []
        
        
        ai_categories = [
            'cs.AI', 'cs.LG', 'cs.CL', 'cs.CV', 'cs.NE', 'cs.RO', 'cs.SE',
            'stat.ML', 'cs.IR', 'cs.MA', 'cs.MM'
        ]
        
        category_query = " OR ".join([f"cat:{cat}" for cat in ai_categories])
        keyword_query = " OR ".join([f"all:{kw}" for kw in keywords])
        
        # Combine keywords with category restrictions
        search_query = f"({keyword_query}) AND ({category_query})"
        
        search = arxiv.Search(
            query=search_query,
            max_results=max_results * 2,  # Fetch more to filter
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        try:
            for result in self.client.results(search):
                
                # title_lower = result.title.lower()
                # abstract_lower = result.summary.lower()
                
                # # Check if any keyword appears in title or abstract
                # keyword_found = any(kw.lower() in title_lower or kw.lower() in abstract_lower 
                #                    for kw in keywords)
                
                # if not keyword_found:
                #     continue
                
                paper = Paper( 
                    arxiv_id=result.entry_id.split('/')[-1],
                    title=result.title,
                    authors=[author.name for author in result.authors],
                    abstract=result.summary,
                    categories=result.categories,
                    published_data=result.published.strftime('%Y-%m-%d'),
                    pdf_url=result.pdf_url,
                    entry_id=result.entry_id
                )
                papers.append(paper)
                
                if len(papers) >= max_results:
                    break
                    
        except Exception as e:
            print(f"Error fetching papers by category: {e}")
            
        return papers
