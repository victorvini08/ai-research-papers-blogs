from typing import List, Dict
from datetime import datetime

def generate_daily_summary_content(papers: List[Dict], date: str) -> str:
    """Generate the content for a daily summary"""
    content = f"# AI Research Papers Summary - {date}\n\n"
    content += f"Today we have **{len(papers)}** interesting AI research papers to share with you. "
    content += "Here's a concise overview of the latest developments in artificial intelligence:\n\n"
    
    # Group papers by category
    categories = {}
    for paper in papers:
        category = paper.get('category', 'General AI')
        if category not in categories:
            categories[category] = []
        categories[category].append(paper)
    
    for category, category_papers in categories.items():
        content += f"## {category}\n\n"
        
        for paper in category_papers[:3]:  # Limit to 3 papers per category
            content += f"### {paper['title']}\n\n"
            content += f"**Authors:** {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}\n\n"
            
            # Use summary if available, otherwise use abstract
            summary_text = paper.get('summary', paper['abstract'])
            if len(summary_text) > 300:
                summary_text = summary_text[:300] + "..."
            
            content += f"{summary_text}\n\n"
            content += f"[Read Full Paper](https://arxiv.org/abs/{paper['arxiv_id']})\n\n"
            content += "---\n\n"
    
    content += "\n*This summary was automatically generated. For more details, click on the paper links above.*"
    
    return content

def generate_blog_summary(papers: List[Dict]) -> str:
    """Generate a concise blog summary for the home page"""
    if not papers:
        return "No recent papers available."
    
    # Get unique categories
    categories = set()
    for paper in papers:
        category = paper.get('category', 'General AI')
        categories.add(category)
    
    # Create a summary
    summary = f"<h1>Latest AI Research Developments</h1>\n\n"
    summary += f"<p>In this week's roundup, we explore <strong>{len(papers)}</strong> groundbreaking AI research papers "
    summary += f"spanning <strong>{len(categories)}</strong> key areas: {', '.join(list(categories)[:3])}"
    if len(categories) > 3:
        summary += f" and more."
    summary += "</p>\n\n"
    
    # Highlight top 3 papers
    summary += "<h2>Key Highlights</h2>\n\n"
    for i, paper in enumerate(papers[:3], 1):
        title = paper['title']
        if len(title) > 80:
            title = title[:80] + "..."
        
        summary += f"<h3>{i}. {title}</h3>\n"
        summary += f"<p><em>By {', '.join(paper['authors'][:2])}{'...' if len(paper['authors']) > 2 else ''}</em></p>\n\n"
        
        # Brief abstract excerpt
        abstract = paper['abstract']
        if len(abstract) > 150:
            abstract = abstract[:150] + "..."
        summary += f"<p>{abstract}</p>\n\n"
    
    if len(papers) > 3:
        summary += f"<p><em>... and {len(papers) - 3} more exciting papers covering the latest advances in AI.</em></p>\n\n"
    
    summary += "<p><strong><a href='/blog'>Read Full Blog Post →</a></strong></p>\n\n"
    summary += "<p><em>This summary was automatically generated from the latest AI research papers.</em></p>"
    
    return summary

def generate_blog_content(papers: List[Dict]) -> str:
    """Generate engaging blog content from recent papers"""
    if not papers:
        return "<h1>No Papers Available</h1><p>No recent papers are available at the moment.</p>"
    
    # Get current date for the blog
    current_date = datetime.now().strftime('%B %d, %Y')
    
    # Group papers by category
    categories = {}
    for paper in papers:
        category = paper.get('category', 'General AI')
        if category not in categories:
            categories[category] = []
        categories[category].append(paper)
    
    # Start building the blog content
    content = f"""
    <div class="blog-header">
        <h1 class="blog-title">🚀 AI Research Roundup: {current_date}</h1>
        <div class="blog-intro">
            <p class="lead">
                Welcome to today's AI research digest! We've curated <strong>{len(papers)}</strong> 
                cutting-edge papers that are pushing the boundaries of artificial intelligence. 
                From breakthrough algorithms to innovative applications, here's what's happening 
                at the forefront of AI research.
            </p>
            <div class="stats-banner">
                <div class="stat-item">
                    <span class="stat-number">{len(papers)}</span>
                    <span class="stat-label">Papers</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{len(categories)}</span>
                    <span class="stat-label">Categories</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{sum(len(papers) for papers in categories.values())}</span>
                    <span class="stat-label">Total</span>
                </div>
            </div>
        </div>
    </div>
    """
    
    # Add category sections
    for category, category_papers in categories.items():
        # Get category icon and description
        category_info = get_category_info(category)
        
        content += f"""
        <div class="category-section">
            <div class="category-header">
                <h2 class="category-title">
                    {category_info['icon']} {category}
                </h2>
                <p class="category-description">{category_info['description']}</p>
            </div>
        """
        
        for i, paper in enumerate(category_papers, 1):
            # Create an engaging paper card
            content += f"""
            <div class="paper-card">
                <div class="paper-header">
                    <div class="paper-number">#{i}</div>
                    <h3 class="paper-title">{paper['title']}</h3>
                </div>
                
                <div class="paper-authors">
                    <i class="fas fa-users"></i>
                    <span>{', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}</span>
                </div>
                
                <div class="paper-abstract">
                    <p>{paper['abstract']}</p>
                </div>
                
                <div class="paper-actions">
                    <a href="https://arxiv.org/abs/{paper['arxiv_id']}" 
                       class="btn btn-primary btn-sm" target="_blank">
                        <i class="fas fa-external-link-alt"></i> Read Paper
                    </a>
                    <a href="https://arxiv.org/pdf/{paper['arxiv_id']}" 
                       class="btn btn-outline-secondary btn-sm" target="_blank">
                        <i class="fas fa-file-pdf"></i> PDF
                    </a>
                    <span class="paper-date">
                        <i class="fas fa-calendar"></i> {paper['published_date']}
                    </span>
                </div>
            </div>
            """
        
        content += "</div>"
    
    # Add conclusion
    content += f"""
    <div class="blog-conclusion">
        <h3>🎯 What's Next?</h3>
        <p>
            These papers represent just a snapshot of the incredible work happening in AI research. 
            Each one contributes to our understanding and capabilities in artificial intelligence, 
            bringing us closer to more intelligent, efficient, and beneficial AI systems.
        </p>
        <p>
            <strong>Stay tuned for more updates!</strong> We'll continue to bring you the latest 
            developments in AI research, helping you stay informed about the technologies that 
            are shaping our future.
        </p>
    </div>
    
    <div class="blog-footer">
        <p><em>This blog was automatically generated from the latest AI research papers. 
        For more details and full papers, click on the links above.</em></p>
    </div>
    """
    
    return content

def get_category_info(category: str) -> Dict:
    """Get category-specific information for better presentation"""
    category_info = {
        "Generative AI & Large Language Models (LLMs)": {
            "icon": "🤖",
            "description": "Breakthroughs in language models, text generation, and creative AI systems"
        },
        "Computer Vision & MultiModal AI": {
            "icon": "👁️",
            "description": "Advances in image recognition, video analysis, and multimodal learning"
        },
        "Agentic AI": {
            "icon": "🤝",
            "description": "Autonomous agents, multi-agent systems, and intelligent decision-making"
        },
        "AI in Healthcare": {
            "icon": "🏥",
            "description": "AI applications in medical diagnosis, drug discovery, and healthcare systems"
        },
        "Explainable & Ethical AI": {
            "icon": "⚖️",
            "description": "Transparency, fairness, and responsible AI development"
        }
    }
    
    return category_info.get(category, {
        "icon": "🔬",
        "description": "Cutting-edge research in artificial intelligence"
    })