#!/usr/bin/env python3
"""
Migration script to convert existing blogs from storing HTML content to storing paper IDs.
This ensures that when paper details change, the blogs reflect those changes.
"""

import sqlite3
import json
import re
from datetime import datetime
from src.database import PaperDatabase
from src.blog import generate_blog_content

def extract_arxiv_ids_from_html(html_content):
    """Extract arxiv IDs from the HTML content of existing blogs"""
    # Look for arxiv.org/abs/ patterns in the HTML, including version suffix
    arxiv_pattern = r'https://arxiv\.org/abs/([0-9]+\.[0-9]+v[0-9]+)'
    matches = re.findall(arxiv_pattern, html_content)
    return list(set(matches))  # Remove duplicates

def migrate_existing_blogs():
    """Migrate existing blogs to the new structure"""
    db = PaperDatabase()
    conn = db._get_connection()
    cursor = conn.cursor()
    
    # Check if we need to migrate
    cursor.execute("PRAGMA table_info(blogs)")
    columns = {row[1] for row in cursor.fetchall()}
    
    if 'paper_ids' not in columns:
        print("Adding paper_ids column to blogs table...")
        try:
            cursor.execute("ALTER TABLE blogs ADD COLUMN paper_ids TEXT DEFAULT '[]'")
            conn.commit()
            print("✓ Added paper_ids column")
        except sqlite3.OperationalError as e:
            print(f"Column might already exist: {e}")
    
    # Get all blogs that don't have paper_ids set
    cursor.execute('''
        SELECT id, title, content, summary, paper_count, categories, published_date, created_at
        FROM blogs 
        WHERE paper_ids IS NULL OR paper_ids = '[]' OR paper_ids = ''
    ''')
    
    blogs_to_migrate = cursor.fetchall()
    print(f"Found {len(blogs_to_migrate)} blogs to migrate...")
    
    migrated_count = 0
    for blog in blogs_to_migrate:
        blog_id, title, content, summary, paper_count, categories, published_date, created_at = blog
        
        if content:
            # Extract arxiv IDs from the HTML content
            arxiv_ids = extract_arxiv_ids_from_html(content)
            
            if arxiv_ids:
                # Update the blog with paper IDs
                cursor.execute('''
                    UPDATE blogs 
                    SET paper_ids = ?
                    WHERE id = ?
                ''', (json.dumps(arxiv_ids), blog_id))
                
                print(f"✓ Migrated blog '{title}' with {len(arxiv_ids)} papers")
                migrated_count += 1
            else:
                print(f"⚠ Could not extract arxiv IDs from blog '{title}'")
        else:
            print(f"⚠ Blog '{title}' has no content to migrate")
    
    conn.commit()
    conn.close()
    
    print(f"\nMigration complete! Migrated {migrated_count} blogs.")
    return migrated_count

def test_dynamic_blog_generation():
    """Test that blogs can be generated dynamically after migration"""
    db = PaperDatabase()
    
    # Get a blog with paper IDs
    blogs = db.get_all_blogs()
    
    if not blogs:
        print("No blogs found to test")
        return
    
    test_blog = blogs[0]
    paper_ids = test_blog.get('paper_ids', [])
    
    if not paper_ids:
        print("No paper IDs found in test blog")
        return
    
    print(f"Testing dynamic generation for blog: {test_blog['title']}")
    print(f"Paper IDs: {paper_ids[:3]}...")  # Show first 3
    
    # Get papers and generate content
    papers = db.get_papers_by_arxiv_ids(paper_ids)
    print(f"Retrieved {len(papers)} papers from database")
    
    if papers:
        # Generate blog content dynamically
        blog_content = generate_blog_content(papers)
        print(f"✓ Successfully generated {len(blog_content)} characters of content")
        
        # Show a preview
        preview = blog_content[:200] + "..." if len(blog_content) > 200 else blog_content
        print(f"Preview: {preview}")
    else:
        print("⚠ No papers found for this blog")

if __name__ == "__main__":
    print("Starting blog migration...")
    print("=" * 50)
    
    try:
        migrated_count = migrate_existing_blogs()
        
        if migrated_count > 0:
            print("\nTesting dynamic blog generation...")
            print("=" * 50)
            test_dynamic_blog_generation()
        
        print("\nMigration completed successfully!")
        print("Blogs will now reflect changes to paper details automatically.")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        import traceback
        traceback.print_exc()
