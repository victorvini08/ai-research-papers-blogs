import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .arxiv_paper_fetcher import PaperFetcher
from .database import PaperDatabase
from .llm_summarizer import LLMSummarizer
from datetime import datetime, timedelta
from .blog import generate_blog_content
logger = logging.getLogger(__name__)

# TODO: We can publish blog in the same scheduler function as well
class PaperFetchScheduler: 
    def __init__(self):
        self.paper_fetcher = PaperFetcher()
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
        logger.info("Starting scheduler for category-based fetching from arXiv and PapersWithCode")
        max_per_category = 3
        all_papers = []
        for category, keywords in self.category_queries.items():
            # Fetch from arXiv
            arxiv_papers = self.paper_fetcher.fetch_papers_by_category(keywords, max_results=max_per_category)
            for paper in arxiv_papers:
                paper.category = category
                paper.source = 'arxiv'
            # Fetch from PapersWithCode
            # pwc_papers = self.pwc_fetcher.fetch_papers_by_category(keywords, max_results=max_per_category)
            # for paper in pwc_papers:
            #     paper.category = category
            #     paper.source = 'paperswithcode'
            all_papers.extend(arxiv_papers)
            #all_papers.extend(pwc_papers)
        # Deduplicate by arxiv_id or title
        seen = set()
        unique_papers = []
        for paper in all_papers:
            key = paper.arxiv_id or paper.title
            if key and key not in seen:
                seen.add(key)
                unique_papers.append(paper)
        logger.info(f"Fetched {len(unique_papers)} unique papers across all categories.")
        # Save to database
        saved_papers = []
        for paper in unique_papers:
            if not self.db.paper_exists(paper.arxiv_id):
                paper_summary = paper.get_summary()
                llm_paper_summary = self.llm_summarizer.summarize_paper(paper_summary, paper)
                paper.summary = llm_paper_summary
                self.db.insert_paper(paper)
                saved_papers.append(paper)
        logger.info(f"Saved {len(saved_papers)} new papers to database.")
        
        # Generate blog content if we have papers
        if saved_papers:
            try:
                blog_content = generate_blog_content(saved_papers)
                blog_title = f"Latest AI Research Papers - {datetime.now().strftime('%B %d, %Y')}"
                blog_summary = f"Discover the latest {len(saved_papers)} AI research papers across {len(set(p.category for p in saved_papers))} categories."
                
                self.db.save_blog(
                    title=blog_title,
                    content=blog_content,
                    summary=blog_summary,
                    paper_count=len(saved_papers),
                    categories=", ".join(set(p.category for p in saved_papers)),
                    published_date=datetime.now().strftime('%Y-%m-%d')
                )
                logger.info(f"Generated and saved blog post with {len(saved_papers)} papers.")
            except Exception as e:
                logger.error(f"Error generating blog content: {e}")
        else:
            logger.info("No new papers to generate blog content for.")
    
    def start(self):
        if self.is_running: 
            logger.info("Scheduler is already running!")
            return
        
        try:
            self.scheduler.add_job(
                    func=self.fetch_and_persist_papers,
                    trigger=CronTrigger(day_of_week='thu',hour=8, minute=0,timezone='Asia/Kolkata'),
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