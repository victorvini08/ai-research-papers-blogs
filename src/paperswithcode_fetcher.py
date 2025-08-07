import requests
from typing import List, Dict
from datetime import datetime

class PapersWithCodeFetcher:
    BASE_URL = "https://paperswithcode.com/api/v1/papers/"

    def __init__(self, api_token: str = None):
        self.api_token = api_token  # Not required for public GET endpoints

    def fetch_papers_by_category(self, keywords: list, max_results: int = 3) -> List[Dict]:
        """
        Fetch papers from PapersWithCode matching any of the provided keywords in title or abstract.
        """
        query = " ".join(keywords)
        params = {
            "q": query,
            "items_per_page": max_results
        }
        headers = {}
        # If you have an API token, you can add: headers['Authorization'] = f'Token {self.api_token}'
        try:
            response = requests.get(self.BASE_URL, params=params, headers=headers, timeout=20)
            response.raise_for_status()
            data = response.json()
            results = []
            for paper in data.get('results', []):
                results.append({
                    'pwc_id': paper.get('id'),
                    'arxiv_id': paper.get('arxiv_id'),
                    'title': paper.get('title'),
                    'authors': paper.get('authors', []),
                    'abstract': paper.get('abstract'),
                    'published_date': paper.get('published'),
                    'url': paper.get('url_abs'),
                    'pdf_url': paper.get('url_pdf'),
                    'code_url': paper.get('url_code'),
                    'tasks': [t['name'] for t in paper.get('tasks', [])] if paper.get('tasks') else [],
                    'repositories': [repo['url'] for repo in paper.get('repositories', [])] if paper.get('repositories') else [],
                })
            return results
        except Exception as e:
            print(f"Error fetching from PapersWithCode API: {e}")
            return []