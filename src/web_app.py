from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime, timedelta
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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

@app.route('/daily-summary')
def daily_summary():
    """Show daily summary of papers"""
    today = datetime.now().strftime('%Y-%m-%d')
    papers = db.get_papers_by_date(today)
    
    if not papers:
        return render_template('daily_summary.html', 
                             papers=[], 
                             date=today,
                             message="No papers found for today.")
    
    return render_template('daily_summary.html', 
                         papers=papers, 
                         date=today)

@app.route('/paper/<arxiv_id>')
def paper_detail(arxiv_id):
    """View detailed information about a specific paper"""
    # Get paper from database
    conn = db._get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT arxiv_id, title, authors, abstract, categories, 
               published_date, summary, category, novelty_score, source
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
        'novelty_score': row[8],
        'source': row[9]
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

@app.route('/papers')
def papers_list():
    """View list of all research papers"""
    # Get all papers ordered by recency
    papers = db.get_recent_papers(days=365)  # Get papers from last year
    return render_template('papers_list.html', papers=papers)

@app.route('/subscribe', methods=['POST'])
def subscribe_email():
    """Handle email subscription"""
    email = request.form.get('email')
    
    if not email:
        flash('Please provide a valid email address.', 'error')
        return redirect(url_for('index'))
    
    try:
        # Save email to database (you'll need to create this table)
        db.save_subscriber_email(email)
        flash('Thank you for subscribing! You\'ll receive our weekly AI research updates.', 'success')
    except Exception as e:
        flash('There was an error processing your subscription. Please try again.', 'error')
        app.logger.error(f"Email subscription error: {e}")
    
    return redirect(url_for('index'))

@app.route('/send-weekly-email')
def send_weekly_email():
    """Send weekly blog email to all subscribers"""
    try:
        # Get the latest blog
        blogs = db.get_all_blogs()
        if not blogs:
            return jsonify({'success': False, 'message': 'No blogs found'})
        
        latest_blog = blogs[0]  # Most recent blog
        
        # Get all subscriber emails
        subscribers = db.get_all_subscriber_emails()
        
        if not subscribers:
            return jsonify({'success': False, 'message': 'No subscribers found'})
        
        # Send email to each subscriber
        sent_count = 0
        for subscriber_email in subscribers:
            if send_blog_email(subscriber_email, latest_blog):
                sent_count += 1
        
        return jsonify({
            'success': True, 
            'message': f'Weekly blog email sent to {sent_count} subscribers',
            'sent_count': sent_count,
            'total_subscribers': len(subscribers)
        })
        
    except Exception as e:
        app.logger.error(f"Weekly email error: {e}")
        return jsonify({'success': False, 'message': f'Error sending emails: {str(e)}'}), 500

@app.route('/unsubscribe')
def unsubscribe():
    """Handle email unsubscription"""
    email = request.args.get('email')
    
    if not email:
        flash('Invalid unsubscribe link.', 'error')
        return redirect(url_for('index'))
    
    try:
        db.unsubscribe_email(email)
        flash('You have been successfully unsubscribed from our weekly updates.', 'success')
    except Exception as e:
        flash('There was an error processing your unsubscription. Please try again.', 'error')
        app.logger.error(f"Email unsubscription error: {e}")
    
    return redirect(url_for('index'))

def send_blog_email(subscriber_email: str, blog: Dict) -> bool:
    """Send a single blog email to a subscriber"""
    try:
        # Email configuration (you'll need to set these environment variables)
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        smtp_username = os.environ.get('SMTP_USERNAME')
        smtp_password = os.environ.get('SMTP_PASSWORD')
        
        if not all([smtp_username, smtp_password]):
            app.logger.error("SMTP credentials not configured")
            return False
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"AI Research Daily - {blog['title']}"
        msg['From'] = smtp_username
        msg['To'] = subscriber_email
        
        # Create HTML content
        html_content = f"""
        <html>
        <body>
            <h2>AI Research Daily - Weekly Update</h2>
            <h3>{blog['title']}</h3>
            <p><strong>Published:</strong> {blog['published_date']}</p>
            <p><strong>Papers Covered:</strong> {blog['paper_count']}</p>
            <hr>
            <div>{blog['summary']}</div>
            <hr>
            <p>Read the full blog post: <a href="{request.host_url}blog/{blog['id']}">Click here</a></p>
            <p>Unsubscribe: <a href="{request.host_url}unsubscribe?email={subscriber_email}">Click here</a></p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_content, 'html'))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        app.logger.error(f"Error sending email to {subscriber_email}: {e}")
        return False

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

@app.route('/health')
def health_check():
    """Simple health check endpoint for deployment platforms"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'AI Research Papers Summarizer'
    })

@app.route('/admin')
def admin_dashboard():
    """Admin dashboard showing system status and controls"""
    try:
        # Get database statistics
        papers_count = len(db.get_recent_papers(days=365))
        blogs_count = len(db.get_all_blogs())
        subscribers_count = len(db.get_all_subscriber_emails())
        
        stats = {
            'papers_count': papers_count,
            'blogs_count': blogs_count,
            'subscribers_count': subscribers_count,
        }
        
        return render_template('admin_dashboard.html', stats=stats)
        
    except Exception as e:
        app.logger.error(f"Error loading admin dashboard: {e}")
        return render_template('admin_dashboard.html', stats={
            'papers_count': 0,
            'blogs_count': 0,
            'subscribers_count': 0,
            'daily_summaries_count': 0
        })

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

@app.route('/api/fetch-and-persist-papers', methods=['POST'])
def fetch_and_persist_papers():
    """API endpoint to manually trigger the full paper fetching and blog generation process"""
    try:
        from .paper_fetch_scheduler import PaperFetchScheduler
        
        # Create a new scheduler instance for manual execution
        manual_scheduler = PaperFetchScheduler()
        
        # Run the full process
        manual_scheduler.fetch_and_persist_papers()
        
        # Get the latest blog to show what was created
        latest_blog = db.get_all_blogs()
        blog_info = latest_blog[0] if latest_blog else None
        
        return jsonify({
            'success': True,
            'message': 'Successfully executed full paper fetching and blog generation process',
            'blog_created': blog_info is not None,
            'latest_blog': blog_info
        })
    
    except Exception as e:
        app.logger.error(f"Error in manual paper fetching: {e}")
        return jsonify({
            'success': False,
            'message': f'Error executing paper fetching process: {str(e)}'
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
