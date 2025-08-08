import logging
from src.paper_fetch_scheduler import PaperFetchScheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()  # Output to console
    ]
)

def main():
    paper_fetcher = PaperFetchScheduler()
    
    papers = paper_fetcher.fetch_and_persist_papers()
    print(papers)
    
if __name__=='__main__':
    main()