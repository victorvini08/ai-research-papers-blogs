import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Database settings
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'database/papers.db')
    
    # arXiv API settings
    ARXIV_MAX_RESULTS = int(os.environ.get('ARXIV_MAX_RESULTS', '50'))
    ARXIV_DELAY_SECONDS = int(os.environ.get('ARXIV_DELAY_SECONDS', '3'))
    ARXIV_NUM_RETRIES = int(os.environ.get('ARXIV_NUM_RETRIES', '3'))
    
    # Paper filtering settings
    RELEVANT_KEYWORDS = [
        'large language model', 'llm', 'transformer', 'attention',
        'neural network', 'deep learning', 'machine learning',
        'artificial intelligence', 'ai', 'natural language',
        'computer vision', 'reinforcement learning', 'generative',
        'foundation model', 'multimodal', 'diffusion', 'gan',
        'bert', 'gpt', 'claude', 'llama', 'chatgpt'
    ]
    
    # AI categories to monitor
    AI_CATEGORIES = [
        'cs.AI', 'cs.LG', 'cs.CL', 'cs.CV', 'cs.NE', 'cs.RO',
        'stat.ML', 'cs.SE'
    ]
    
    # Summary generation settings
    MAX_PAPERS_PER_SUMMARY = int(os.environ.get('MAX_PAPERS_PER_SUMMARY', '10'))
    MAX_ABSTRACT_LENGTH = int(os.environ.get('MAX_ABSTRACT_LENGTH', '300'))
    
    # Web app settings
    PAPERS_PER_PAGE = int(os.environ.get('PAPERS_PER_PAGE', '12'))
    SUMMARIES_PER_PAGE = int(os.environ.get('SUMMARIES_PER_PAGE', '10'))
