import requests
import os
import time
from typing import List, Dict
from .paper import Paper
import logging

# Delay sentence_transformers import to avoid CUDA issues in production
# Only import when actually needed

logger = logging.getLogger(__name__)


class PaperQualityFilter:
    """Filter papers based on author h-index and institution importance"""

    def __init__(self):
        # Read API key from environment if provided
        self.semantic_scholar_api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
        # Use Graph API (recommended)
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        # Rate-limiting configuration
        self.request_sleep_sec = float(os.getenv("SEMANTIC_SCHOLAR_SLEEP", "0.6"))
        self.api_retry_max = int(os.getenv("SEMANTIC_SCHOLAR_MAX_RETRIES", "3"))
        self.api_backoff_base = float(os.getenv("SEMANTIC_SCHOLAR_BACKOFF_BASE", "1.8"))
        # In-memory cache to avoid duplicate lookups
        self._author_cache: Dict[str, Dict] = {}
        self.prestigious_institutions = {
            # Tech Companies
            'openai', 'microsoft', 'google', 'meta', 'apple', 'amazon', 'nvidia', 'intel', 'ibm',
            'deepmind', 'anthropic', 'cohere', 'hugging face', 'stability ai', 'midjourney',

            # Universities
            'stanford', 'mit', 'harvard', 'berkeley', 'cmu', 'princeton', 'yale', 'columbia',
            'university of oxford', 'university of cambridge', 'tsinghua',

            # # Research Labs
            # 'bell labs', 'xerox parc', 'sri international', 'allen institute', 'max planck institute',
            # 'cnrs', 'fraunhofer', 'national institutes of health', 'nsf', 'darpa',

            # Other Notable
            'netflix', 'spotify', 'uber', 'lyft', 'airbnb', 'salesforce', 'adobe', 'autodesk'
        }

        # Institution name variations and aliases
        self.institution_aliases = {
            'stanford university': 'stanford',
            'massachusetts institute of technology': 'mit',
            'harvard university': 'harvard',
            'university of california berkeley': 'berkeley',
            'carnegie mellon university': 'cmu',
            'princeton university': 'princeton',
            'yale university': 'yale',
            'columbia university': 'columbia',
            'university of toronto': 'university of toronto',
            'university of oxford': 'university of oxford',
            'university of cambridge': 'university of cambridge',
            'tsinghua university': 'tsinghua',
            'national university of singapore': 'nus',
            'google research': 'google',
            'microsoft research': 'microsoft',
            'intel labs': 'intel',
            'nvidia research': 'nvidia',
            'meta ai research': 'meta',
            'apple machine learning': 'apple',
            'amazon web services': 'amazon',
            'netflix research': 'netflix',
            'spotify research': 'spotify',
            'uber ai': 'uber',
            'lyft level 5': 'lyft',
            'salesforce research': 'salesforce',
            'adobe research': 'adobe',
            'airbnb data science': 'airbnb',
            'autodesk research': 'autodesk'
        }

    def filter_papers(self, papers: List[Paper]) -> List[Paper]:
        """Filter papers based on quality criteria and assign quality scores"""
        logger.info(f"Filtering {len(papers)} papers based on quality criteria")

        for i in range(len(papers)):
            paper = papers[i]
            try:
                logger.info(f"Filtering paper {i} of {len(papers)}")
                # Get author information from Semantic Scholar
                author_info = self.get_authors_info(paper.authors)

                # Calculate quality score
                quality_score = self.calculate_quality_score(paper, author_info)
                paper.quality_score = quality_score

                # Add author metadata to paper
                paper.author_h_indices = author_info.get('h_indices', [])
                paper.author_institutions = author_info.get('institutions', [])

            except Exception as e:
                logger.error(f"Error processing paper {paper.arxiv_id}: {e}")
                paper.quality_score = 0.0
                paper.author_h_indices = []
                paper.author_institutions = []

        # Sort papers by quality score
        papers.sort(key=lambda x: x.quality_score, reverse=True)

        # Filter out papers with very low quality scores
        filtered_papers = [p for p in papers if p.quality_score > 0.15]
        
        logger.info(f"Filtered to {len(filtered_papers)} high-quality papers")
        return filtered_papers

    def get_authors_info(self, author_names: List[str]) -> Dict:
        """Get author information from Semantic Scholar API"""
        h_indices = []
        institutions = []

        for author_name in author_names[:5]:  # Limit to first 5 authors to avoid API rate limits
            try:
                # Use cache when available
                if author_name in self._author_cache:
                    author_info = self._author_cache[author_name]
                else:
                    author_info = self.search_author(author_name)
                    # Cache even None to avoid hammering the API repeatedly for the same name
                    self._author_cache[author_name] = author_info
                if author_info:
                    h_index = author_info.get('hIndex', 0)
                    h_indices.append(h_index)

                    # Get institution information
                    if 'affiliations' in author_info and author_info['affiliations'] is not None:
                        aff_value = author_info['affiliations']
                        # Normalize affiliations which could be a string, dict, or list of those
                        normalized: List[str] = []
                        if isinstance(aff_value, str):
                            normalized.append(aff_value)
                        elif isinstance(aff_value, dict):
                            name = aff_value.get('name', '')
                            if name:
                                normalized.append(name)
                        elif isinstance(aff_value, list):
                            for item in aff_value:
                                if isinstance(item, str):
                                    normalized.append(item)
                                elif isinstance(item, dict):
                                    name = item.get('name', '')
                                    if name:
                                        normalized.append(name)
                        for inst_name in normalized:
                            inst_lower = inst_name.strip().lower()
                            if inst_lower:
                                institutions.append(inst_lower)

                # Rate limiting
                time.sleep(self.request_sleep_sec)

            except Exception as e:
                logger.warning(f"Could not fetch info for author {author_name}: {e}")
                continue

        return {
            'h_indices': h_indices,
            'institutions': institutions
        }

    def search_author(self, author_name: str) -> Dict:
        """Search for author in Semantic Scholar"""
        url = f"{self.base_url}/author/search"
        params = {
            'query': author_name,
            'limit': 1,
            # Request fields we need for scoring
            'fields': 'hIndex,affiliations'
        }
        headers = {}
        if self.semantic_scholar_api_key:
            headers['x-api-key'] = self.semantic_scholar_api_key

        attempt = 0
        while attempt < self.api_retry_max:
            try:
                response = requests.get(url, params=params, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('data'):
                        return data['data'][0]
                    return None
                if response.status_code == 429:
                    # Respect Retry-After if present, otherwise exponential backoff
                    retry_after = response.headers.get('Retry-After')
                    if retry_after is not None:
                        try:
                            delay = float(retry_after)
                        except ValueError:
                            delay = (self.api_backoff_base ** attempt) * self.request_sleep_sec
                    else:
                        delay = (self.api_backoff_base ** attempt) * self.request_sleep_sec
                    logger.warning(
                        f"Rate limited by Semantic Scholar for '{author_name}'. Sleeping {delay:.2f}s before retry {attempt + 1}/{self.api_retry_max}.")
                    time.sleep(delay)
                    attempt += 1
                    continue
                # Other non-200s: log and break
                try:
                    err = response.json()
                except Exception:
                    err = {'error': response.text}
                logger.warning(f"Semantic Scholar API non-200 ({response.status_code}) for '{author_name}': {err}")
                return None
            except Exception as e:
                logger.warning(f"Error searching for author {author_name}: {e}")
                return None
        return None

    def calculate_quality_score(self, paper: Paper, author_info: Dict) -> float:
        """Calculate quality score based on multiple factors"""
        score = 0.0

        # Factor 1: Author h-index (40% weight)
        h_indices = author_info.get('h_indices', [])
        if h_indices:
            avg_h_index = sum(h_indices) / len(h_indices)
            # Normalize h-index (0-100 scale)
            h_score = min(avg_h_index / 50.0, 1.0)
            score += h_score * 0.7
        
        # Factor 2: Institution prestige (30% weight)
        institutions = author_info.get('institutions', [])
        institution_score = 0.0
        for inst in institutions:
            if self.is_prestigious_institution(inst):
                institution_score = 1.0
                break
        score += institution_score * 0.3
        
        
        # TODO: We can calculate category relevance by semantic similarity between paper details and category keywords
        # Factor 3: Category relevance (10% weight)
        # All papers are pre-filtered by category, so they get full score
        # category_score = 1.0 * 0.1
        # score += category_score
        
        return score

    def is_prestigious_institution(self, institution_name: str) -> bool:
        """Check if institution is prestigious"""
        institution_lower = institution_name.lower()

        # Check exact matches
        if institution_lower in self.prestigious_institutions:
            return True

        # Check aliases
        if institution_lower in self.institution_aliases:
            return True

        # Check partial matches for major institutions
        for prestigious in self.prestigious_institutions:
            if prestigious in institution_lower or institution_lower in prestigious:
                return True

        return False

    def calculate_cosine_score(self, unique_papers: List[Paper], categories:Dict[str, List[str]]):
        """Calculate cosine similarity between paper text and categories using TF-IDF (no external APIs)"""
        import numpy as np
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        try:
            logger.info("Using TF-IDF for cosine similarity (no external APIs needed)")
            
            def get_tfidf_embeddings(texts):
                """Get TF-IDF embeddings"""
                # Initialize TF-IDF vectorizer
                vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=(1, 2),
                    min_df=1,
                    max_df=0.95,
                    lowercase=True
                )
                
                # Fit and transform texts
                tfidf_matrix = vectorizer.fit_transform(texts)
                logger.info(f"TF-IDF matrix shape: {tfidf_matrix.shape}")
                
                return tfidf_matrix
            
            # Prepare category texts
            category_texts = []
            category_names = list(categories.keys())

            for category, keywords in categories.items():
                category_text = f"{category} {' '.join(keywords)}"
                category_texts.append(category_text)

            # Combine all texts for vectorization
            all_texts = category_texts + [f"{paper.title} {paper.abstract}" for paper in unique_papers if not paper.category_cosine_scores]
            
            if not all_texts:
                logger.info("No papers need category scores")
                return
            
            logger.info(f"Processing {len(all_texts)} texts with TF-IDF...")
            
            # Get TF-IDF embeddings for all texts
            tfidf_matrix = get_tfidf_embeddings(all_texts)
            
            # Extract category vectors (first len(categories) rows)
            category_vectors = tfidf_matrix[:len(categories)]
            
            # Extract paper vectors (remaining rows)
            paper_vectors = tfidf_matrix[len(categories):]
            
            # Calculate similarities for each paper
            paper_idx = 0
            for i, paper in enumerate(unique_papers):
                if paper.category_cosine_scores:
                    continue
                
                if paper_idx >= len(paper_vectors):
                    break
                
                logger.info(f"Calculating similarity for paper {i + 1} of {len(unique_papers)}")
                
                # Get paper vector
                paper_vector = paper_vectors[paper_idx:paper_idx+1]
                
                # Calculate cosine similarity with all categories
                similarities = cosine_similarity(paper_vector, category_vectors).flatten()
                
                # Store scores
                paper.category_cosine_scores = {
                    category: float(score) for category, score in zip(category_names, similarities)
                }
                
                # Set the category to the one with highest similarity
                best_category_idx = np.argmax(similarities)
                paper.category = category_names[best_category_idx]
                
                logger.info(f"Paper {i + 1} scores: {paper.category_cosine_scores}")
                
                paper_idx += 1
                
        except Exception as e:
            logger.error(f"Error during Groq API embedding calculation: {e}")
            raise
