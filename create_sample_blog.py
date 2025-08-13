#!/usr/bin/env python3
"""
Script to create a sample blog post for testing
"""

from src.arxiv_paper_fetcher import PaperFetcher
from src.database import PaperDatabase
from src.blog import generate_blog_content, generate_blog_summary
from datetime import datetime
import json

def create_sample_blog():
    """Create a sample blog post"""
    
    print("🚀 Creating Sample Blog Post")
    print("=" * 40)
    
    # Initialize components
    paper_fetcher = PaperFetcher()
    db = PaperDatabase()
    
    # Get recent papers
    recent_papers = db.get_recent_papers(days=30)
    
    if not recent_papers:
        print("❌ No papers found in database")
        print("💡 Run demo_fetch_papers.py first to add some papers")
        return
    
    # Take the 10 most recent papers
    papers = recent_papers[:10]
    print(f"✅ Using {len(papers)} papers for blog generation")
    
    # Generate blog content
    blog_title = f"Latest AI Research Roundup - {datetime.now().strftime('%B %d, %Y')}"
    blog_content = generate_blog_content(papers)
    blog_summary = generate_blog_summary(papers)
    
    # Get categories
    categories = set()
    for paper in papers:
        category = paper.category or 'General AI'
        categories.add(category)
    categories_str = ', '.join(list(categories))
    
    # Save blog to database
    db.save_blog(
        title=blog_title,
        content=blog_content,
        summary=blog_summary,
        paper_count=len(papers),
        categories=categories_str,
        published_date=datetime.now().strftime('%Y-%m-%d')
    )
    
    print(f"✅ Blog saved successfully!")
    print(f"📝 Title: {blog_title}")
    print(f"📊 Papers: {len(papers)}")
    print(f"🏷️  Categories: {categories_str}")
    
    # Show blog preview
    print("\n📖 Blog Summary Preview:")
    print("-" * 40)
    lines = blog_summary.split('\n')
    for line in lines[:10]:
        if line.strip():
            print(f"   {line}")
    if len(lines) > 10:
        print("   ...")
    
    print("\n" + "=" * 40)
    print("🎉 Sample blog created successfully!")
    print("🌐 Visit http://localhost:5000 to see the blog")
    print("📚 Visit http://localhost:5000/blog to see all blogs")

if __name__ == "__main__":
    create_sample_blog() 