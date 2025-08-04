from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime, timedelta
import os
from typing import List, Dict
from .paper_fetcher import PaperFetcher
from .database import PaperDatabase

app = Flask(__name__, template_folder='../templates')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Initialize components
paper_fetcher = PaperFetcher()
db = PaperDatabase()

@app.route('/')
def index():
    """Home page showing the latest blog and recent papers"""
    # Get all blogs ordered by recency
    blogs = db.get_all_blogs()
    
    # Get the 10 most recent papers
    recent_papers = db.get_recent_papers(days=30)  # Get papers from last 30 days
    papers = recent_papers[:10]  # Limit to 10 most recent
    
    return render_template('index.html', 
                         blogs=blogs,
                         papers=papers)

@app.route('/daily/<date>')
def daily_summary(date):
    """View daily summary for a specific date"""
    daily_summary = db.get_daily_summary(date)
    papers = db.get_papers_by_date(date)
    
    if not daily_summary:
        return render_template('404.html', message="No summary found for this date"), 404
    
    return render_template('daily_summary.html', 
                         daily_summary=daily_summary,
                         papers=papers,
                         summary_date=date)

@app.route('/paper/<arxiv_id>')
def paper_detail(arxiv_id):
    """View detailed information about a specific paper"""
    # Get paper from database
    conn = db._get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT arxiv_id, title, authors, abstract, categories, 
               published_date, summary, category, novelty_score
        FROM papers 
        WHERE arxiv_id = ?
    ''', (arxiv_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return render_template('404.html', message="Paper not found"), 404
    
    paper = {
        'arxiv_id': row[0],
        'title': row[1],
        'authors': eval(row[2]) if row[2] else [],
        'abstract': row[3],
        'categories': eval(row[4]) if row[4] else [],
        'published_date': row[5],
        'summary': row[6],
        'category': row[7],
        'novelty_score': row[8]
    }
    
    return render_template('paper_detail.html', paper=paper)

@app.route('/blog')
def blog_list():
    """View list of all blogs"""
    blogs = db.get_all_blogs()
    return render_template('blog_list.html', blogs=blogs)

@app.route('/blog/<int:blog_id>')
def blog_detail(blog_id):
    """View a specific blog post"""
    blog = db.get_blog_by_id(blog_id)
    if not blog:
        return render_template('404.html', message="Blog post not found"), 404
    
    return render_template('blog_detail.html', blog=blog)

@app.route('/archive')
def archive():
    """View archive of all daily summaries"""
    # Get all daily summaries
    conn = db._get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT date, paper_count, created_at
        FROM daily_summaries 
        ORDER BY date DESC
    ''')
    
    summaries = []
    for row in cursor.fetchall():
        summaries.append({
            'date': row[0],
            'paper_count': row[1],
            'created_at': row[2]
        })
    
    conn.close()
    
    return render_template('archive.html', summaries=summaries)

@app.route('/api/fetch-papers', methods=['POST'])
def fetch_papers():
    """API endpoint to manually trigger paper fetching"""
    try:
        # Fetch recent papers
        papers = paper_fetcher.fetch_recent_papers(max_results=50)
        
        # Filter relevant papers
        relevant_papers = paper_fetcher.filter_relevant_papers(papers)
        
        # Save to database
        saved_count = 0
        for paper in relevant_papers:
            if db.insert_paper(paper):
                saved_count += 1
        
        return jsonify({
            'success': True,
            'message': f'Successfully fetched and saved {saved_count} papers',
            'total_fetched': len(papers),
            'relevant_saved': saved_count
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching papers: {str(e)}'
        }), 500

@app.route('/api/generate-summary', methods=['POST'])
def generate_summary():
    """API endpoint to generate daily summary"""
    try:
        data = request.get_json()
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # Get papers for the date
        papers = db.get_papers_by_date(date)
        
        if not papers:
            return jsonify({
                'success': False,
                'message': f'No papers found for date {date}'
            }), 404
        
        # Generate summary content
        summary_content = generate_daily_summary_content(papers, date)
        
        # Save to database
        db.save_daily_summary(date, summary_content, len(papers))
        
        return jsonify({
            'success': True,
            'message': f'Successfully generated summary for {date}',
            'paper_count': len(papers)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating summary: {str(e)}'
        }), 500

def generate_blog_content(papers: List[Dict]) -> str:
    """Generate blog content from recent papers"""
    content = f"<h1>Latest AI Research Papers Blog</h1>\n\n"
    content += f"<p>Welcome to our latest blog covering <strong>{len(papers)}</strong> cutting-edge AI research papers! "
    content += "We've curated the most interesting developments in artificial intelligence to keep you updated.</p>\n\n"
    
    # Group papers by category
    categories = {}
    for paper in papers:
        category = paper.get('category', 'General AI')
        if category not in categories:
            categories[category] = []
        categories[category].append(paper)
    
    for category, category_papers in categories.items():
        content += f"<h2>{category}</h2>\n\n"
        
        for paper in category_papers:
            content += f"<h3>{paper['title']}</h3>\n\n"
            content += f"<p><strong>Authors:</strong> {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}</p>\n\n"
            
            # Use only abstract, not summary
            abstract_text = paper['abstract']
            if len(abstract_text) > 250:
                abstract_text = abstract_text[:250] + "..."
            
            content += f"<p>{abstract_text}</p>\n\n"
            content += f"<p><a href='https://arxiv.org/abs/{paper['arxiv_id']}' target='_blank'>Read Full Paper</a></p>\n\n"
            content += "<hr>\n\n"
    
    content += "\n<p><em>This blog was automatically generated from the latest AI research papers. For more details, click on the paper links above.</em></p>"
    
    return content

def generate_blog_summary(papers: List[Dict]) -> str:
    """Generate a concise blog summary for the home page"""
    if not papers:
        return "No recent papers available."
    
    # Get unique categories
    categories = set()
    for paper in papers:
        category = paper.get('category', 'General AI')
        categories.add(category)
    
    # Create a summary
    summary = f"<h1>Latest AI Research Developments</h1>\n\n"
    summary += f"<p>In this week's roundup, we explore <strong>{len(papers)}</strong> groundbreaking AI research papers "
    summary += f"spanning <strong>{len(categories)}</strong> key areas: {', '.join(list(categories)[:3])}"
    if len(categories) > 3:
        summary += f" and more."
    summary += "</p>\n\n"
    
    # Highlight top 3 papers
    summary += "<h2>Key Highlights</h2>\n\n"
    for i, paper in enumerate(papers[:3], 1):
        title = paper['title']
        if len(title) > 80:
            title = title[:80] + "..."
        
        summary += f"<h3>{i}. {title}</h3>\n"
        summary += f"<p><em>By {', '.join(paper['authors'][:2])}{'...' if len(paper['authors']) > 2 else ''}</em></p>\n\n"
        
        # Brief abstract excerpt
        abstract = paper['abstract']
        if len(abstract) > 150:
            abstract = abstract[:150] + "..."
        summary += f"<p>{abstract}</p>\n\n"
    
    if len(papers) > 3:
        summary += f"<p><em>... and {len(papers) - 3} more exciting papers covering the latest advances in AI.</em></p>\n\n"
    
    summary += "<p><strong><a href='/blog'>Read Full Blog Post →</a></strong></p>\n\n"
    summary += "<p><em>This summary was automatically generated from the latest AI research papers.</em></p>"
    
    return summary

def generate_daily_summary_content(papers: List[Dict], date: str) -> str:
    """Generate the content for a daily summary"""
    content = f"# AI Research Papers Summary - {date}\n\n"
    content += f"Today we have **{len(papers)}** interesting AI research papers to share with you. "
    content += "Here's a concise overview of the latest developments in artificial intelligence:\n\n"
    
    # Group papers by category
    categories = {}
    for paper in papers:
        category = paper.get('category', 'General AI')
        if category not in categories:
            categories[category] = []
        categories[category].append(paper)
    
    for category, category_papers in categories.items():
        content += f"## {category}\n\n"
        
        for paper in category_papers[:3]:  # Limit to 3 papers per category
            content += f"### {paper['title']}\n\n"
            content += f"**Authors:** {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}\n\n"
            
            # Use summary if available, otherwise use abstract
            summary_text = paper.get('summary', paper['abstract'])
            if len(summary_text) > 300:
                summary_text = summary_text[:300] + "..."
            
            content += f"{summary_text}\n\n"
            content += f"[Read Full Paper](https://arxiv.org/abs/{paper['arxiv_id']})\n\n"
            content += "---\n\n"
    
    content += "\n*This summary was automatically generated. For more details, click on the paper links above.*"
    
    return content

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
