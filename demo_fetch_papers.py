#!/usr/bin/env python3
"""
Demo script to fetch papers and generate a summary
"""

import arxiv
def demo_fetch_and_summarize():
    search_query = "all:computer vision"
    client = arxiv.Client(
            page_size=100,
            delay_seconds=3,
            num_retries=3
        )
    search = arxiv.Search(
            query=search_query,
            max_results=20,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
    print(next(client.results(search)))
                
if __name__ == "__main__":
    demo_fetch_and_summarize() 