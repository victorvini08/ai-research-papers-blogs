#!/usr/bin/env python3
"""
Standalone script to run category cosine scores backfill
"""

import logging
import sys
import os

# Add src to path
sys.path.append('src')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Run the backfill process"""
    try:
        logger.info("🚀 Starting category cosine scores backfill...")
        
        # Import after path setup
        from src.backfill_data import BackfillData
        from src.database import PaperDatabase
        
        # Check current state
        db = PaperDatabase()
        papers = db.get_all_papers()
        
        logger.info(f"📊 Found {len(papers)} total papers")
        logger.info(f"📊 Found {len(papers)} papers needing backfill")
        
        logger.info("🔄 Running backfill...")
        BackfillData().backfill_category_cosine_scores(papers)
        logger.info("✅ Backfill completed successfully!")
            
    except Exception as e:
        logger.error(f"❌ Error during backfill: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
