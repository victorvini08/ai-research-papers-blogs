import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class PaperDatabase:
    def __init__(self, db_path: str = "database/papers.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Papers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                arxiv_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                authors TEXT NOT NULL,
                abstract TEXT NOT NULL,
                categories TEXT NOT NULL,
                published_date TEXT NOT NULL,
                summary TEXT,
                category TEXT,
                novelty_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Daily summaries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE NOT NULL,
                summary_content TEXT NOT NULL,
                paper_count INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Blogs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blogs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                summary TEXT NOT NULL,
                paper_count INTEGER NOT NULL,
                categories TEXT,
                published_date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Processing log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processing_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                arxiv_id TEXT NOT NULL,
                status TEXT NOT NULL,
                error_message TEXT,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def paper_exists(self, arxiv_id: str) -> bool:
        """Check if a paper already exists in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM papers WHERE arxiv_id = ?", (arxiv_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    def insert_paper(self, paper_data: Dict) -> bool:
        """Insert a new paper into the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO papers (
                    arxiv_id, title, authors, abstract, categories, 
                    published_date, summary, category, novelty_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                paper_data['arxiv_id'],
                paper_data['title'],
                json.dumps(paper_data['authors']),
                paper_data['abstract'],
                json.dumps(paper_data['categories']),
                paper_data['published_date'],
                paper_data.get('summary', ''),
                paper_data.get('category', ''),
                paper_data.get('novelty_score', 0.0)
            ))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # Paper already exists
            return False
        except Exception as e:
            print(f"Error inserting paper: {e}")
            return False
    
    def get_papers_by_date(self, date: str) -> List[Dict]:
        """Get all papers published on a specific date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT arxiv_id, title, authors, abstract, categories, 
                   published_date, summary, category, novelty_score
            FROM papers 
            WHERE DATE(published_date) = ?
            ORDER BY novelty_score DESC
        ''', (date,))
        
        papers = []
        for row in cursor.fetchall():
            papers.append({
                'arxiv_id': row[0],
                'title': row[1],
                'authors': json.loads(row[2]),
                'abstract': row[3],
                'categories': json.loads(row[4]),
                'published_date': row[5],
                'summary': row[6],
                'category': row[7],
                'novelty_score': row[8]
            })
        
        conn.close()
        return papers
    
    def get_recent_papers(self, days: int = 7) -> List[Dict]:
        """Get papers from the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT arxiv_id, title, authors, abstract, categories, 
                   published_date, summary, category, novelty_score
            FROM papers 
            WHERE DATE(published_date) >= DATE('now', '-{} days')
            ORDER BY published_date DESC, novelty_score DESC
        '''.format(days))
        
        papers = []
        for row in cursor.fetchall():
            papers.append({
                'arxiv_id': row[0],
                'title': row[1],
                'authors': json.loads(row[2]),
                'abstract': row[3],
                'categories': json.loads(row[4]),
                'published_date': row[5],
                'summary': row[6],
                'category': row[7],
                'novelty_score': row[8]
            })
        
        conn.close()
        return papers
    
    def update_paper_summary(self, arxiv_id: str, summary: str, category: str, novelty_score: float):
        """Update paper with generated summary and categorization"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE papers 
            SET summary = ?, category = ?, novelty_score = ?, updated_at = CURRENT_TIMESTAMP
            WHERE arxiv_id = ?
        ''', (summary, category, novelty_score, arxiv_id))
        
        conn.commit()
        conn.close()
    
    def save_daily_summary(self, date: str, summary_content: str, paper_count: int):
        """Save the daily summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO daily_summaries (date, summary_content, paper_count)
            VALUES (?, ?, ?)
        ''', (date, summary_content, paper_count))
        
        conn.commit()
        conn.close()
    
    def get_daily_summary(self, date: str) -> Optional[Dict]:
        """Get daily summary for a specific date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT summary_content, paper_count, created_at
            FROM daily_summaries 
            WHERE date = ?
        ''', (date,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'summary_content': row[0],
                'paper_count': row[1],
                'created_at': row[2]
            }
        return None
    
    def log_processing(self, arxiv_id: str, status: str, error_message: str = None):
        """Log processing status for debugging"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO processing_log (arxiv_id, status, error_message)
            VALUES (?, ?, ?)
        ''', (arxiv_id, status, error_message))
        
        conn.commit()
        conn.close()
    
    def save_blog(self, title: str, content: str, summary: str, paper_count: int, categories: str, published_date: str):
        """Save a new blog post"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO blogs (title, content, summary, paper_count, categories, published_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, content, summary, paper_count, categories, published_date))
        
        conn.commit()
        conn.close()
    
    def get_all_blogs(self) -> List[Dict]:
        """Get all blogs ordered by recency"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, summary, paper_count, categories, published_date, created_at
            FROM blogs 
            ORDER BY created_at DESC
        ''')
        
        blogs = []
        for row in cursor.fetchall():
            blogs.append({
                'id': row[0],
                'title': row[1],
                'summary': row[2],
                'paper_count': row[3],
                'categories': row[4],
                'published_date': row[5],
                'created_at': row[6]
            })
        
        conn.close()
        return blogs
    
    def get_blog_by_id(self, blog_id: int) -> Optional[Dict]:
        """Get a specific blog by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, content, summary, paper_count, categories, published_date, created_at
            FROM blogs 
            WHERE id = ?
        ''', (blog_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'summary': row[3],
                'paper_count': row[4],
                'categories': row[5],
                'published_date': row[6],
                'created_at': row[7]
            }
        return None
    
    def _get_connection(self):
        """Get database connection for internal use"""
        return sqlite3.connect(self.db_path)
