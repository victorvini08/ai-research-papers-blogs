import logging
from src.database import PaperDatabase
from src.paper_quality_filter import PaperQualityFilter
from src.paper import Paper

logger = logging.getLogger(__name__)

class BackfillData:
    def __init__(self):
        self.database = PaperDatabase()
        self.paper_quality_filter = PaperQualityFilter()
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
                "healthcare", "medical imaging", "disease diagnosis", "radiology", "clinical", "drug discovery", "biomedical"
            ],
            "Explainable & Ethical AI": [
                "explainable", "interpretability", "fairness", "ethics", "responsible ai", "bias", "transparency"
            ]
        }

    def backfill_category_cosine_scores(self):
        papers = self.database.get_all_papers()
        self.paper_quality_filter.calculate_cosine_score(papers, self.category_queries)
        for i in range(len(papers)):
            paper = papers[i]
            fields = {'category_cosine_scores': paper.category_cosine_scores, 'category': paper.category}
            self.database.update_paper_fields(
                arxiv_id=paper.arxiv_id,
                fields=fields
            )
            logger.info(f"Updated paper number {i} of total {len(papers)} with category cosine scores")