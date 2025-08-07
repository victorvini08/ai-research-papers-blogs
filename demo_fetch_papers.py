#!/usr/bin/env python3
"""
Demo script to fetch papers and generate a summary
"""

from src.arxiv_paper_fetcher import PaperFetcher
from src.database import PaperDatabase
from datetime import datetime
import json

def demo_fetch_and_summarize():
    """Demonstrate fetching papers and generating a summary"""
    
    print("🚀 AI Research Papers Daily - Demo")
    print("=" * 50)
    
    # Initialize components
    paper_fetcher = PaperFetcher()
    db = PaperDatabase()
    
    print("\n1. Fetching recent papers from arXiv...")
    try:
        # Fetch papers (limit to 10 for demo)
        papers = paper_fetcher.fetch_recent_papers(max_results=10)
        print(f"✅ Fetched {len(papers)} papers from arXiv")
        
        # Filter relevant papers
        relevant_papers = paper_fetcher.filter_relevant_papers(papers)
        print(f"✅ Found {len(relevant_papers)} relevant papers")
        
        # Save to database
        saved_count = 0
        for paper in relevant_papers:
            if db.insert_paper(paper):
                saved_count += 1
        
        print(f"✅ Saved {saved_count} papers to database")
        
        # Show sample papers
        if relevant_papers:
            print("\n📄 Sample papers:")
            for i, paper in enumerate(relevant_papers[:3]):
                print(f"   {i+1}. {paper['title'][:60]}...")
                print(f"      Authors: {', '.join(paper['authors'][:2])}{'...' if len(paper['authors']) > 2 else ''}")
                print(f"      Categories: {', '.join(paper['categories'][:2])}")
                print()
        
    except Exception as e:
        print(f"❌ Error fetching papers: {e}")
        return
    
    print("\n2. Generating daily summary...")
    try:
        # Get today's papers
        today = datetime.now().strftime('%Y-%m-%d')
        today_papers = db.get_papers_by_date(today)
        
        if today_papers:
            # Generate summary content
            from src.web_app import generate_daily_summary_content
            summary_content = generate_daily_summary_content(today_papers, today)
            
            # Save summary
            db.save_daily_summary(today, summary_content, len(today_papers))
            print(f"✅ Generated summary for {today} with {len(today_papers)} papers")
            
            # Show summary preview
            print("\n📝 Summary preview:")
            lines = summary_content.split('\n')
            for line in lines[:10]:  # Show first 10 lines
                if line.strip():
                    print(f"   {line}")
            if len(lines) > 10:
                print("   ...")
        else:
            print(f"ℹ️  No papers found for {today}")
            
    except Exception as e:
        print(f"❌ Error generating summary: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed!")
    print("🌐 Open http://localhost:5000 to view the web application")
    print("📊 Check the archive page to see all summaries")

if __name__ == "__main__":
    demo_fetch_and_summarize() 