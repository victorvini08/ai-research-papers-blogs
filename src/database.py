import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from .paper import Paper

def _parse_summary_field(summary_field):
    """Helper function to parse summary field from database"""
    if not summary_field:
        return None
    try:
        if summary_field.startswith('{'):
            return json.loads(summary_field)
        else:
            return summary_field
    except (json.JSONDecodeError, AttributeError):
        return summary_field

class PaperDatabase:
    def __init__(self, db_path: str = None):
        # Allow overriding via env var for deploys with volumes
        env_db_path = os.environ.get('DATABASE_PATH')
        self.db_path = env_db_path or db_path or "database/papers.db"
        # Ensure parent directory exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
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
                source TEXT,
                quality_score REAL DEFAULT 0.0,
                author_h_indices TEXT,
                author_institutions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Ensure missing columns exist for legacy databases
        cursor.execute("PRAGMA table_info(papers)")
        existing_columns = {row[1] for row in cursor.fetchall()}

        # Columns to ensure with their ALTER TABLE statements
        migrations = []
        if 'quality_score' not in existing_columns:
            migrations.append("ALTER TABLE papers ADD COLUMN quality_score REAL DEFAULT 0.0")
        if 'author_h_indices' not in existing_columns:
            migrations.append("ALTER TABLE papers ADD COLUMN author_h_indices TEXT DEFAULT '[]'")
        if 'author_institutions' not in existing_columns:
            migrations.append("ALTER TABLE papers ADD COLUMN author_institutions TEXT DEFAULT '[]'")
        if 'created_at' not in existing_columns:
            migrations.append("ALTER TABLE papers ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        if 'updated_at' not in existing_columns:
            migrations.append("ALTER TABLE papers ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

        for stmt in migrations:
            try:
                cursor.execute(stmt)
            except sqlite3.OperationalError:
                # Ignore if add fails due to race/other
                pass
        
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
        
        # Subscribers table for email notifications
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscribers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
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
    
    def insert_paper(self, paper: Paper) -> bool:
        """Insert a new paper into the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO papers (
                    arxiv_id, title, authors, abstract, categories, 
                    published_date, summary, category, novelty_score, source,
                    quality_score, author_h_indices, author_institutions
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                paper.arxiv_id,
                paper.title,
                json.dumps(paper.authors),
                paper.abstract,
                json.dumps(paper.categories),
                paper.published_data,
                json.dumps(paper.summary) if isinstance(paper.summary, dict) else (paper.summary or ''),
                paper.category or '',
                paper.novelty_score or 0.0,
                paper.source or 'arxiv',
                paper.quality_score or 0.0,
                json.dumps(paper.author_h_indices) if paper.author_h_indices else '[]',
                json.dumps(paper.author_institutions) if paper.author_institutions else '[]'
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
    
    def insert_paper_dict(self, paper_data: Dict) -> bool:
        """Insert a new paper from dictionary (for backward compatibility)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO papers (
                    arxiv_id, title, authors, abstract, categories, 
                    published_date, summary, category, novelty_score, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                paper_data['arxiv_id'],
                paper_data['title'],
                json.dumps(paper_data['authors']),
                paper_data['abstract'],
                json.dumps(paper_data['categories']),
                paper_data['published_date'],
                paper_data.get('summary', ''),
                paper_data.get('category', ''),
                paper_data.get('novelty_score', 0.0),
                paper_data.get('source', 'arxiv')
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
    
    def get_papers_by_date(self, date: str) -> List[Paper]:
        """Get all papers published on a specific date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT arxiv_id, title, authors, abstract, categories, 
                   published_date, summary, category, novelty_score, source
            FROM papers 
            WHERE DATE(published_date) = ?
            ORDER BY novelty_score DESC
        ''', (date,))
        
        papers = []
        for row in cursor.fetchall():
            paper = Paper(
                arxiv_id=row[0],
                title=row[1],
                authors=json.loads(row[2]),
                abstract=row[3],
                categories=json.loads(row[4]),
                published_data=row[5],
                pdf_url=f"https://arxiv.org/pdf/{row[0]}",
                entry_id=f"https://arxiv.org/abs/{row[0]}",
                summary=_parse_summary_field(row[6]),
                category=row[7],
                novelty_score=row[8],
                source=row[9]
            )
            papers.append(paper)
        
        conn.close()
        return papers
    
    def get_recent_papers(self, days: int = 7) -> List[Paper]:
        """Get papers from the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT arxiv_id, title, authors, abstract, categories, 
                   published_date, summary, category, novelty_score, source
            FROM papers 
            WHERE DATE(published_date) >= DATE('now', '-{} days')
            ORDER BY published_date DESC, novelty_score DESC
        '''.format(days))
        
        papers = []
        for row in cursor.fetchall():
            paper = Paper(
                arxiv_id=row[0],
                title=row[1],
                authors=json.loads(row[2]),
                abstract=row[3],
                categories=json.loads(row[4]),
                published_data=row[5],
                pdf_url=f"https://arxiv.org/pdf/{row[0]}",
                entry_id=f"https://arxiv.org/abs/{row[0]}",
                summary=_parse_summary_field(row[6]),
                category=row[7],
                novelty_score=row[8],
                source=row[9]
            )
            papers.append(paper)
        
        conn.close()
        return papers
    
    def update_paper_summary(self, arxiv_id: str, summary: str, category: str, novelty_score: float):
        """Update paper with generated summary and categorization"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert summary to JSON if it's a dictionary
        summary_json = json.dumps(summary) if isinstance(summary, dict) else summary
        
        cursor.execute('''
            UPDATE papers 
            SET summary = ?, category = ?, novelty_score = ?, updated_at = CURRENT_TIMESTAMP
            WHERE arxiv_id = ?
        ''', (summary_json, category, novelty_score, arxiv_id))
        
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
    
    def save_subscriber_email(self, email: str) -> bool:
        """Save a new subscriber email"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO subscribers (email, subscribed_at, is_active)
                VALUES (?, CURRENT_TIMESTAMP, 1)
            ''', (email,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving subscriber email: {e}")
            return False
    
    def get_all_subscriber_emails(self) -> List[str]:
        """Get all active subscriber emails"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT email FROM subscribers WHERE is_active = 1')
        emails = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return emails
    
    def unsubscribe_email(self, email: str) -> bool:
        """Unsubscribe an email address"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE subscribers SET is_active = 0 WHERE email = ?
            ''', (email,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error unsubscribing email: {e}")
            return False
    
    def save_blog(self, title, content, summary, paper_count, categories, published_date):
        """Save a new blog post"""
      
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO blogs (title, content, summary, paper_count, categories, published_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, content, summary, paper_count, categories, published_date))
        
        conn.commit()
        conn.close()
        return cursor.lastrowid
    
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
