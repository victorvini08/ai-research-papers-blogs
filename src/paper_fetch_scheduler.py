import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .arxiv_paper_fetcher import PaperFetcher
from .paper_quality_filter import PaperQualityFilter
from .database import PaperDatabase
from .llm_summarizer import LLMSummarizer
from datetime import datetime, timedelta
from .blog import generate_blog_content
logger = logging.getLogger(__name__)

class PaperFetchScheduler: 
    def __init__(self):
        self.paper_fetcher = PaperFetcher()
        self.paper_quality_filter = PaperQualityFilter()
        self.db = PaperDatabase()
        self.llm_summarizer = LLMSummarizer()
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        self.category_queries = {
            "Generative AI & LLMs": [
                "large language model", "llm", "gpt", "transformer"
            ],
            "Computer Vision & MultiModal AI": [
                "computer vision", "image", "vision", "multimodal", "multi-modal", "video", "segmentation"
            ],
            "Agentic AI": [
                "agent", "agentic", "autonomous agent", "multi-agent", "rl", "reinforcement learning"
            ],
            "AI in healthcare": [
                "healthcare", "drug discovery", "biomedical", "clinical"
            ],
            "Explainable & Ethical AI": [
                "explainable", "interpretability", "fairness", "ethics", "responsible ai", "bias", "transparency"
            ]
        }
        
    def fetch_and_persist_papers(self):
        logger.info("Starting scheduler for category-based fetching from arXiv")
        max_per_category = 20
        all_papers = []
        for category, keywords in self.category_queries.items():
            logger.info(f"Fetching papers for category: {category}")
            # Fetch from arXiv
            arxiv_papers = self.paper_fetcher.fetch_papers_by_category(keywords, max_results=max_per_category)
            for paper in arxiv_papers:
                paper.category = category
                paper.source = 'arxiv'
            all_papers.extend(arxiv_papers)
            logger.info(f"Fetched {len(arxiv_papers)} papers for {category}")
        # Deduplicate by arxiv_id or title
        seen = set()
        unique_papers = []
        for paper in all_papers:
            key = paper.arxiv_id or paper.title
            if key and key not in seen:
                seen.add(key)
                if not self.db.paper_exists(paper.arxiv_id):
                    unique_papers.append(paper)
        logger.info(f"Fetched {len(unique_papers)} unique papers across all categories.")
        
        # Filter papers based on quality criteria
        filtered_papers = self.paper_quality_filter.filter_papers(unique_papers)
        logger.info(f"After quality filtering: {len(filtered_papers)} papers")
        
        # Select top papers for blog (aim for 15-20 papers total)
        selected_papers = self.select_top_papers_for_blog(filtered_papers, target_count=15)
        logger.info(f"Selected {len(selected_papers)} top papers for blog")
        
        # Save selected papers to database
        saved_papers = []
        for paper in selected_papers:
            if not self.db.paper_exists(paper.arxiv_id):
                try:
                    paper_summary = paper.get_summary()
                    llm_paper_summary = self.llm_summarizer.summarize_paper(paper_summary, paper)
                    paper.summary = llm_paper_summary
                    self.db.insert_paper(paper)
                    saved_papers.append(paper)
                except Exception as e:
                    logger.error(f"Error processing paper {paper.arxiv_id}: {e}")
                    continue
        logger.info(f"Saved {len(saved_papers)} new papers to database.")
        
        # Generate blog content if we have papers
        if saved_papers:
            try:
                blog_content = generate_blog_content(saved_papers)
                blog_title = f"Weekly AI Research Roundup - {datetime.now().strftime('%B %d, %Y')}"
                blog_summary = f"Discover the latest {len(saved_papers)} AI research papers across {len(set(p.category for p in saved_papers))} categories."
                
                blog_id = self.db.save_blog(
                    title=blog_title,
                    content=blog_content,
                    summary=blog_summary,
                    paper_count=len(saved_papers),
                    categories=", ".join(set(p.category for p in saved_papers)),
                    published_date=datetime.now().strftime('%Y-%m-%d')
                )
                
                logger.info(f"Generated and saved blog post with ID {blog_id} containing {len(saved_papers)} papers.")
                
                # Send weekly email to subscribers
                self.send_weekly_blog_email(blog_id)
            except Exception as e:
                logger.error(f"Error generating blog content: {e}")
        else:
            logger.info("No new papers to generate blog content for.")
    
    
    def select_top_papers_for_blog(self, papers, target_count=15):
        """Select top papers for the weekly blog, ensuring category balance"""
        # Group papers by category
        category_papers = {}
        for paper in papers:
            category = paper.category
            if category not in category_papers:
                category_papers[category] = []
            category_papers[category].append(paper)
        
        # Sort papers within each category by quality score
        for category in category_papers:
            category_papers[category].sort(key=lambda x: getattr(x, 'quality_score', 0), reverse=True)
        
        # Select papers ensuring category balance
        selected_papers = []
        papers_per_category = max(1, target_count // len(category_papers))
        
        for category, papers_list in category_papers.items():
            # Take top papers from each category
            selected_from_category = papers_list[:papers_per_category]
            selected_papers.extend(selected_from_category)
        
        # If we have room for more papers, add from categories with highest quality papers
        remaining_slots = target_count - len(selected_papers)
        if remaining_slots > 0:
            # Get all papers sorted by quality score
            all_papers_sorted = sorted(papers, key=lambda x: getattr(x, 'quality_score', 0), reverse=True)
            
            # Add remaining papers, avoiding duplicates
            selected_ids = {p.arxiv_id for p in selected_papers}
            for paper in all_papers_sorted:
                if len(selected_papers) >= target_count:
                    break
                if paper.arxiv_id not in selected_ids:
                    selected_papers.append(paper)
                    selected_ids.add(paper.arxiv_id)
        
        return selected_papers[:target_count]
    
    def send_weekly_blog_email(self, blog_id):
        """Send the weekly blog email to all subscribers"""
        try:
            # First try direct function call (more reliable)
            if self._send_weekly_email_direct():
                return True
            
            # Fallback to HTTP call if direct method fails
            return self._send_weekly_email_http()
            
        except Exception as e:
            logger.error(f"Error sending weekly email: {e}")
            return False
    
    def _send_weekly_email_direct(self):
        """Send weekly email by calling the function directly"""
        try:
            from .web_app import send_blog_email
            
            # Get the latest blog
            blogs = self.db.get_all_blogs()
            if not blogs:
                logger.warning("No blogs found for email")
                return False
            
            latest_blog = blogs[0]  # Most recent blog
            
            # Get all subscriber emails
            subscribers = self.db.get_all_subscriber_emails()
            
            if not subscribers:
                logger.warning("No subscribers found for email")
                return False
            
            # Send email to each subscriber
            sent_count = 0
            for subscriber_email in subscribers:
                if send_blog_email(subscriber_email, latest_blog):
                    sent_count += 1
            
            logger.info(f"Weekly blog email sent directly to {sent_count}/{len(subscribers)} subscribers")
            return sent_count > 0
            
        except Exception as e:
            logger.error(f"Direct email sending failed: {e}")
            return False
    
    def _send_weekly_email_http(self):
        """Send weekly email via HTTP call (fallback method)"""
        try:
            import requests
            import os
            
            # Determine the correct URL for the environment
            if os.environ.get('FLY_APP_NAME'):
                # Production environment - use the app's public URL
                app_name = os.environ.get('FLY_APP_NAME')
                base_url = f"https://{app_name}.fly.dev"
            else:
                # Development environment
                base_url = "http://localhost:5000"
            
            # Call the email endpoint
            email_url = f"{base_url}/send-weekly-email"
            logger.info(f"Calling email endpoint: {email_url}")
            
            response = requests.get(email_url, timeout=30)
            if response.status_code == 200:
                logger.info("Weekly blog email sent successfully via HTTP")
                return True
            else:
                logger.error(f"Failed to send weekly email via HTTP: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"HTTP email sending failed: {e}")
            return False
    
    def start(self):
        if self.is_running: 
            logger.info("Scheduler is already running!")
            return
        
        try:
            self.scheduler.add_job(
                    func=self.fetch_and_persist_papers,
                    trigger=CronTrigger(day_of_week='tue',hour=23, minute=33,timezone='Asia/Kolkata'),
                    id='weekly_paper_fetch',
                    name='Weekly Research Papers Fetch',
                    replace_existing=True,
                    max_instances=1,  # Prevent overlapping jobs
                    misfire_grace_time=3600  # Allow 1 hour grace period
                )
            
            self.scheduler.start()
            self.is_running = True
            logger.info("Paper fetching scheduler started successfully")
        except Exception as e:
            logger.error("Failed to start Paper Fetching Scheduler: ", e)
            
    def stop(self):
        if self.is_running:
            try:
                self.scheduler.shutdown()
                self.is_running = False
                logger.info("Paper fetching scheduler stopped successfully")
            except Exception as e:
                logger.error("Failed to stop Paper Fetching Scheduler: ", e)
                
    def get_scheduler_health(self):
        if not self.is_running:
            return {"status": "Stopped"}
        
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time,
                "trigger": str(job.trigger),
            })
        return {"status": "Running", "jobs": jobs}
    
    def __del__(self):
        self.stop()
    
paper_scheduler = PaperFetchScheduler()

def initialize_scheduler():
    """Initialize the paper fetching scheduler"""
    try:
        paper_scheduler.start()
        logger.info("Paper Fetch Scheduler initialized")
        
    except Exception as e:
        logger.error("Failed to initialize scheduler: ",e)

def shutdown_scheduler():
    """Shutdown the scheduler gracefully"""
    try:
        paper_scheduler.stop()
        logger.info("Scheduler shutdown complete")
    except Exception as e:
        logger.error("Failed to shutdown scheduler: ", e)