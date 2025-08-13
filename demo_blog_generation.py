#!/usr/bin/env python3
"""
Demo script to show automatic blog generation from recent papers
"""

from src.arxiv_paper_fetcher import PaperFetcher
from src.database import PaperDatabase
from src.blog import generate_blog_content
from datetime import datetime
import json

def demo_blog_generation():
    """Demonstrate automatic blog generation from recent papers"""
    
    print("🚀 AI Research Papers Daily - Blog Generation Demo")
    print("=" * 60)
    
    # Initialize components
    paper_fetcher = PaperFetcher()
    db = PaperDatabase()
    
    print("\n1. Checking for recent papers in database...")
    try:
        # Get recent papers from database
        recent_papers = db.get_recent_papers(days=30)
        print("Recent paper summary: ",recent_papers[0].summary)
        print(f"✅ Found {len(recent_papers)} papers in database from last 30 days")
        
        if recent_papers:
            # Get the 10 most recent papers
            papers = recent_papers[:10]
            print(f"✅ Using the {len(papers)} most recent papers for blog generation")
            
            # Show sample papers
            print("\n📄 Sample papers for blog:")
            for i, paper in enumerate(papers[:3]):
                print(f"   {i+1}. {paper.title[:60]}...")
                print(f"      Authors: {', '.join(paper.authors[:2])}{'...' if len(paper.authors) > 2 else ''}")
                print(f"      Date: {paper.published_data}")
                print()
            
            print("\n2. Generating blog content automatically...")
            # Generate blog content
            blog_content = generate_blog_content(papers)
            
            print(f"✅ Blog generated successfully!")
            print(f"📝 Blog length: {len(blog_content)} characters")
            
            # Show blog preview
            print("\n📖 Blog Preview:")
            print("-" * 50)
            lines = blog_content.split('\n')
            for line in lines[:15]:  # Show first 15 lines
                if line.strip():
                    print(f"   {line}")
            if len(lines) > 15:
                print("   ...")
            print("-" * 50)
            
            # Show statistics
            print("\n📊 Blog Statistics:")
            categories = {}
            for paper in papers:
                category = paper.category or 'General AI'
                if category not in categories:
                    categories[category] = 0
                categories[category] += 1
            
            for category, count in categories.items():
                print(f"   • {category}: {count} papers")
            
            all_authors = []
            for paper in papers:
                for author in paper.authors:
                    if author not in all_authors:
                        all_authors.append(author)
            
            print(f"   • Total unique authors: {len(all_authors)}")
            print(f"   • Total papers covered: {len(papers)}")
            
        else:
            print("ℹ️  No papers found in database")
            print("💡 You can run demo_fetch_papers.py to add some papers first")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Blog generation demo completed!")
    print("🌐 Open http://localhost:5000 to see the live blog")
    print("📝 The blog is automatically generated from the 10 most recent papers")
    print("🔄 The blog updates automatically when new papers are added")

if __name__ == "__main__":
    demo_blog_generation() 