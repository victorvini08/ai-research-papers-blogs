#!/usr/bin/env python3
"""
Memory-efficient backfill script for category cosine scores
"""

import os
import sys
import logging
import gc
import psutil
from src.database import PaperDatabase
from src.paper_quality_filter import PaperQualityFilter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def main():
    """Main backfill function with memory monitoring"""
    logger.info("🚀 Starting memory-efficient category cosine scores backfill...")
    
    try:
        # Initialize database and filter
        db = PaperDatabase()
        filter_instance = PaperQualityFilter()
        
        # Get all papers
        all_papers = db.get_all_papers()
        logger.info(f"📊 Found {len(all_papers)} total papers")
        
        # Filter papers that need backfill
        papers_needing_backfill = [p for p in all_papers if not p.category_cosine_scores]
        logger.info(f"📊 Found {len(papers_needing_backfill)} papers needing backfill")
        
        if not papers_needing_backfill:
            logger.info("✅ All papers already have category cosine scores")
            return
        
        # Define categories
        categories = {
            'Generative AI & LLMs': ['language model', 'transformer', 'gpt', 'llm', 'generative', 'text generation', 'natural language'],
            'Computer Vision & MultiModal AI': ['computer vision', 'image', 'video', 'multimodal', 'visual', 'detection', 'segmentation'],
            'Agentic AI': ['agent', 'autonomous', 'planning', 'reasoning', 'decision making', 'multi-agent'],
            'AI in healthcare': ['medical', 'healthcare', 'clinical', 'diagnosis', 'treatment', 'patient', 'biomedical'],
            'Explainable & Ethical AI': ['explainable', 'interpretable', 'fairness', 'bias', 'ethics', 'transparency', 'responsible']
        }
        
        # Process papers in very small batches
        batch_size = 3  # Very small batch size for memory efficiency
        total_batches = (len(papers_needing_backfill) + batch_size - 1) // batch_size
        
        logger.info(f"🔄 Processing {len(papers_needing_backfill)} papers in {total_batches} batches of {batch_size}")
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(papers_needing_backfill))
            batch_papers = papers_needing_backfill[start_idx:end_idx]
            
            logger.info(f"📦 Processing batch {batch_num + 1}/{total_batches} (papers {start_idx + 1}-{end_idx})")
            logger.info(f"💾 Memory usage before batch: {get_memory_usage():.1f} MB")
            
            try:
                # Calculate cosine scores for this batch
                filter_instance.calculate_cosine_score(batch_papers, categories)
                
                # Save batch to database
                for paper in batch_papers:
                    db.update_paper_category_scores(paper.arxiv_id, paper.category, paper.category_cosine_scores)
                
                logger.info(f"✅ Batch {batch_num + 1} completed successfully")
                logger.info(f"💾 Memory usage after batch: {get_memory_usage():.1f} MB")
                
            except Exception as e:
                logger.error(f"❌ Error processing batch {batch_num + 1}: {e}")
                continue
            
            # Force garbage collection after each batch
            gc.collect()
            
            # Small delay to allow memory cleanup
            import time
            time.sleep(0.5)
        
        logger.info("🎉 Memory-efficient backfill completed!")
        logger.info(f"💾 Final memory usage: {get_memory_usage():.1f} MB")
        
    except Exception as e:
        logger.error(f"❌ Backfill failed: {e}")
        raise

if __name__ == "__main__":
    main()
