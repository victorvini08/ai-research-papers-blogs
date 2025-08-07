from src.paper_fetcher import PaperFetcher

def main():
    paper_fetcher = PaperFetcher()
    
    paper_data = {
        'arxiv_id': '2507.23676v1',
        'title': 'DepMicroDiff: Diffusion-Based Dependency-Aware Multimodal Imputation for Microbiome Data',
        
    }
    paper_summary = paper_fetcher.summarize_paper(paper_data)
    print(paper_summary)
    
if __name__=='__main__':
    main()