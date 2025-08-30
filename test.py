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
    papers = db.get_recent_papers(days=70)
    categories = {
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
            "healthcare", "medical imaging", "disease diagnosis", "radiology", "clinical", "drug discovery",
            "biomedical"
        ],
        "Explainable & Ethical AI": [
            "explainable", "interpretability", "fairness", "ethics", "responsible ai", "bias", "transparency"
        ]
    }
    paper_quality_filter = PaperQualityFilter()
    paper_quality_filter.calculate_cosine_score(papers[:10], categories)

    for i in range(10):
        print("+++++++++++++++++++++++++++++++++++++")
        print("category of ppr is: ", papers[i].category)
        print("title of ppr is:", papers[i].title)
        print("abstract of ppr is:", papers[i].abstract)
        print("score of ppr is:", papers[i].category_cosine_scores)
        print("+++++++++++++++++++++++++++++++++++++")


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