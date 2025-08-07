import arxiv
import requests
import feedparser
import tempfile
import PyPDF2
from datetime import datetime, timedelta
from typing import List, Dict
import time
import re

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
    
    def fetch_recent_papers(self, max_results: int = 50) -> List[Dict]:
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
                paper_data = {
                    'arxiv_id': result.entry_id.split('/')[-1],
                    'title': result.title,
                    'authors': [author.name for author in result.authors],
                    'abstract': result.summary,
                    'categories': result.categories,
                    'published_date': result.published.strftime('%Y-%m-%d'),
                    'pdf_url': result.pdf_url,
                    'entry_id': result.entry_id
                }
                papers.append(paper_data)
                
                # Add delay to be respectful to arXiv servers
                time.sleep(1)
                
        except Exception as e:
            print(f"Error fetching papers: {e}")
        
        return papers
    
    def fetch_papers_by_date(self, date: str) -> List[Dict]:
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
                    paper_data = {
                        'arxiv_id': result.entry_id.split('/')[-1],
                        'title': result.title,
                        'authors': [author.name for author in result.authors],
                        'abstract': result.summary,
                        'categories': result.categories,
                        'published_date': result.published.strftime('%Y-%m-%d'),
                        'pdf_url': result.pdf_url,
                        'entry_id': result.entry_id
                    }
                    papers.append(paper_data)
                
                # Stop if we've gone past our target date
                if paper_date < target_date.date():
                    break
                    
                time.sleep(1)
                
        except Exception as e:
            print(f"Error fetching papers for date {date}: {e}")
        
        return papers
    
    def filter_relevant_papers(self, papers: List[Dict]) -> List[Dict]:
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
            title_lower = paper['title'].lower()
            abstract_lower = paper['abstract'].lower()
            
            # Check if paper contains relevant keywords
            relevance_score = 0
            for keyword in relevant_keywords:
                if keyword in title_lower or keyword in abstract_lower:
                    relevance_score += 1
            
            # Keep papers with at least one relevant keyword
            if relevance_score > 0:
                paper['relevance_score'] = relevance_score
                relevant_papers.append(paper)
        
        # Sort by relevance score
        relevant_papers.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return relevant_papers[:30]  # Limit to top 30 most relevant papers
    
    def get_paper_metadata(self, arxiv_id: str) -> Dict:
        """Get detailed metadata for a specific paper"""
        try:
            search = arxiv.Search(id_list=[arxiv_id])
            result = next(self.client.results(search))
            
            return {
                'arxiv_id': arxiv_id,
                'title': result.title,
                'authors': [author.name for author in result.authors],
                'abstract': result.summary,
                'categories': result.categories,
                'published_date': result.published.strftime('%Y-%m-%d'),
                'pdf_url': result.pdf_url,
                'entry_id': result.entry_id
            }
        except Exception as e:
            print(f"Error fetching metadata for {arxiv_id}: {e}")
            return None
        
    def download_paper(self, paper_url: str) -> str:
        """Download a paper"""
        try: 
            response = requests.get(paper_url, timeout=30)
            response.raise_for_status()
            
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            tmp_file.write(response.content)
            tmp_file.close()
            return tmp_file.name
            
        except requests.RequestException as e:
            raise Exception(f"Failed to download PDF: {str(e)}")
    
    def summarize_paper(self, paper_data: Dict) -> str:
        """Summarize a paper"""
        paper_url = f"https://arxiv.org/pdf/{paper_data['arxiv_id']}"
        pdf_path = self.download_paper(paper_url)
        
        try:
            content = {}
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                if pdf_reader.metadata:
                    content['metadata'] = {
                        'title': pdf_reader.metadata.get('/Title', ''),
                        'author': pdf_reader.metadata.get('/Author', ''),
                        'subject': pdf_reader.metadata.get('/Subject', ''),
                        'creator': pdf_reader.metadata.get('/Creator', ''),
                        'producer': pdf_reader.metadata.get('/Producer', ''),
                        'creation_date': pdf_reader.metadata.get('/CreationDate', ''),
                        'modification_date': pdf_reader.metadata.get('/ModDate', '')
                    }
                print("TESTING")
                full_text = ""
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    full_text += page.extract_text() + "\n"
                
                content['full_text'] = full_text
            
        except Exception as e:
            print("Error occured while reading pdf: ", e)

    def fetch_papers_by_category(self, keywords: list, max_results: int = 3) -> List[Dict]:
        """
        Fetch papers from arXiv matching any of the provided keywords in title or abstract.
        """
        papers = []
        
        
        # Build a search query that combines keywords with category restrictions
        category_query = "cat:cs"
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
                
                paper_data = {
                    'arxiv_id': result.entry_id.split('/')[-1],
                    'title': result.title,
                    'authors': [author.name for author in result.authors],
                    'abstract': result.summary,
                    'categories': result.categories,
                    'published_date': result.published.strftime('%Y-%m-%d'),
                    'pdf_url': result.pdf_url,
                    'entry_id': result.entry_id
                }
                papers.append(paper_data)
                
                if len(papers) >= max_results:
                    break
                    
        except Exception as e:
            print(f"Error fetching papers by category: {e}")
            
        return papers
