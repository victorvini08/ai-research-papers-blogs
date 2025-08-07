from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime, timedelta
import os
from typing import List, Dict
from .arxiv_paper_fetcher import PaperFetcher
from .paper_fetch_scheduler import paper_scheduler, initialize_scheduler, shutdown_scheduler
from .database import PaperDatabase
from .blog import generate_daily_summary_content, generate_blog_summary, generate_blog_content

app = Flask(__name__, template_folder='../templates')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

paper_fetcher = PaperFetcher()
db = PaperDatabase()

with app.app_context():
    try:
        initialize_scheduler()
    except Exception as e:
        app.logger.error(f"Failed to start paper fetching scheduler: {e}")
        
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

@app.route('/api/scheduler-health')
def scheduler_health():
    """API endpoint to check scheduler health"""
    return jsonify(paper_scheduler.get_scheduler_health())

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





if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
