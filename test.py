import logging
from src.paper_fetch_scheduler import PaperFetchScheduler
from src.arxiv_paper_fetcher import PaperFetcher
from src.blog import generate_blog_content
from src.database import PaperDatabase
from src.paper import Paper
import json
import sqlite3
from datetime import datetime
from src.paper_quality_filter import PaperQualityFilter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()  # Output to console
    ]
)

def main():
    db = PaperDatabase()
    papers = db.get_all_papers()
    
    for paper in papers[:10]:
        print(paper.title, paper.category, paper.category_cosine_scores)
    

    # count = 0
    # for paper in papers:
    #     paper_summary = paper.get_summary()
    #     with open(f'output_{count}.json', 'w') as f:
    #         json.dump(paper_summary, f)
    #     count +=1
    # # paper_fetcher = PaperFetchScheduler()
    
    # paper_fetcher.fetch_and_persist_papers()
    # db_path =  "database/papers.db"
    # conn = sqlite3.connect(db_path)
    # cursor = conn.cursor()
    #
    # # Query to get last 9 papers ordered by creation time (newest first)
    # query = """
    #     SELECT
    #         id, arxiv_id, title, authors, abstract, categories,
    #         published_date, summary, category, novelty_score,
    #         source, created_at, updated_at
    #     FROM papers
    #     ORDER BY created_at DESC
    #     LIMIT 9
    # """
    #
    # cursor.execute(query)
    # papers = []
    # for row in cursor.fetchall():
    #     paper = Paper(
    #         arxiv_id=row[1],
    #         title=row[2],
    #         authors=json.loads(row[3]),
    #         abstract=row[4],
    #         categories=json.loads(row[5]),
    #         published_data=row[6],
    #         pdf_url=f"https://arxiv.org/pdf/{row[1]}",
    #         entry_id=f"https://arxiv.org/abs/{row[1]}",
    #         summary=row[7],
    #         category=row[8],
    #         novelty_score=row[9],
    #         source=row[10]
    #     )
    #     papers.append(paper)
    #
    # conn.close()
    # blog_content = generate_blog_content(papers)
    # blog_title = f"Latest AI Research Papers - {datetime.now().strftime('%B %d, %Y')}"
    # blog_summary = f"Discover the latest {len(papers)} AI research papers across {len(set(p.category for p in papers))} categories."
    #
    # db.save_blog(
    #             title=blog_title,
    #             content=blog_content,
    #             summary=blog_summary,
    #             paper_count=len(saved_papers),
    #             categories=", ".join(set(p.category for p in saved_papers)),
    #             published_date=datetime.now().strftime('%Y-%m-%d')
    #             )
if __name__=='__main__':
    main()