from typing import List, Dict
from datetime import datetime
from .paper import Paper
from .llm_summarizer import LLMSummarizer
import markdown2

def generate_daily_summary_content(papers: List[Paper], date: str) -> str:
    """Generate the content for a daily summary"""
    content = f"# AI Research Papers Summary - {date}\n\n"
    content += f"Today we have **{len(papers)}** interesting AI research papers to share with you. "
    content += "Here's a concise overview of the latest developments in artificial intelligence:\n\n"
    
    # Group papers by category
    categories = {}
    for paper in papers:
        category = paper.category or 'General AI'
        if category not in categories:
            categories[category] = []
        categories[category].append(paper)
    
    for category, category_papers in categories.items():
        content += f"## {category}\n\n"
        
        for paper in category_papers[:3]:  # Limit to 3 papers per category
            content += f"### {paper.title}\n\n"
            content += f"**Authors:** {', '.join(paper.authors[:3])}{'...' if len(paper.authors) > 3 else ''}\n\n"
            
            # Use summary if available, otherwise use abstract
            summary_text = paper.summary or paper.abstract
            if len(summary_text) > 300:
                summary_text = summary_text[:300] + "..."
            
            content += f"{summary_text}\n\n"
            content += f"[Read Full Paper](https://arxiv.org/abs/{paper.arxiv_id})\n\n"
            content += "---\n\n"
    
    content += "\n*This summary was automatically generated. For more details, click on the paper links above.*"
    
    return content

def generate_blog_summary(papers: List[Paper]) -> str:
    """Generate a concise blog summary for the home page"""
    if not papers:
        return "No recent papers available."
    
    # Get unique categories
    categories = set()
    for paper in papers:
        category = paper.category or 'General AI'
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
        title = paper.title
        if len(title) > 80:
            title = title[:80] + "..."
        
        summary += f"<h3>{i}. {title}</h3>\n"
        summary += f"<p><em>By {', '.join(paper.authors[:2])}{'...' if len(paper.authors) > 2 else ''}</em></p>\n\n"
        
        # Brief abstract excerpt
        abstract = paper.abstract
        if len(abstract) > 150:
            abstract = abstract[:150] + "..."
        summary += f"<p>{abstract}</p>\n\n"
    
    if len(papers) > 3:
        summary += f"<p><em>... and {len(papers) - 3} more exciting papers covering the latest advances in AI.</em></p>\n\n"
    
    summary += "<p><strong><a href='/blog'>Read Full Blog Post →</a></strong></p>\n\n"
    summary += "<p><em>This summary was automatically generated from the latest AI research papers.</em></p>"
    
    return summary

def render_structured_summary(summary_dict):
    """Render structured LLM summary in a 2x2 grid layout"""
    # Section display order and icons for 2x2 grid
    section_order = [
        ("key problem", "🧩", "Key Problem"),
        ("problem", "🧩", "Problem"),
        ("main problem", "🧩", "Main Problem"),
        ("challenge", "🧩", "Challenge"),
        ("key innovation", "💡", "Key Innovation"),
        ("innovation", "💡", "Innovation"),
        ("novelty", "💡", "Novelty"),
        ("contribution", "💡", "Contribution"),
        ("practical impact", "🌍", "Practical Impact"),
        ("impact", "🌍", "Impact"),
        ("real-world impact", "🌍", "Real-world Impact"),
        ("implications", "🌍", "Implications"),
        ("analogy", "🔍", "Analogy"),
        ("intuitive explanation", "🔍", "Intuitive Explanation"),
        ("analogy / intuitive explanation", "🔍", "Analogy / Intuitive Explanation"),
    ]
    # Lowercase keys for matching
    summary_keys = {k.lower(): k for k in summary_dict.keys()}
    html = '<div class="llm-summary-grid">'
    shown = set()
    for key, icon, label in section_order:
        if key in summary_keys and key not in shown:
            section_content = summary_dict[summary_keys[key]].strip()
            if section_content:
                html += f'''<div class="summary-section">
                    <h4>{icon} {label}</h4>
                    <div>{markdown2.markdown(section_content)}</div>
                </div>'''
                shown.add(key)
    # Render any extra sections not in the order
    for k, v in summary_dict.items():
        lk = k.lower()
        if lk not in shown and lk != "summary" and v.strip():
            html += f'''<div class="summary-section">
                <h4>📝 {k.title()}</h4>
                <div>{markdown2.markdown(v.strip())}</div>
            </div>'''
    # If only a generic 'summary' key, show it
    if not shown and "summary" in summary_dict:
        html += f'<div class="summary-section">{markdown2.markdown(summary_dict["summary"])}</div>'
    html += '</div>'
    return html

def generate_blog_content(papers: List[Paper]) -> str:
    """Generate engaging blog content from recent papers"""
    if not papers:
        return "<h1>No Papers Available</h1><p>No recent papers are available at the moment.</p>"
    
    current_date = datetime.now().strftime('%B %d, %Y')
    categories = {}
    for paper in papers:
        category = paper.category or 'General AI'
        if category not in categories:
            categories[category] = []
        categories[category].append(paper)
    
    content = f"""
    <div class="blog-header">
        <h1 class="blog-title"> AI Research Roundup: {current_date}</h1>
        <div class="blog-intro">
            <p class="lead">Discover the latest breakthroughs in artificial intelligence with our curated selection of top cutting-edge research papers of this week.</p>
        </div>
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
                <span class="stat-number">{len(set([author for paper in papers for author in paper.authors]))}</span>
                <span class="stat-label">Researchers</span>
            </div>
        </div>
    </div>
    """
    for category, category_papers in categories.items():
        category_info = get_category_info(category)
        content += f"""
        <div class="category-section">
            <div class="category-header">
                <h2 class="category-title">{category_info['icon']} {category}</h2>
                <p class="category-description">{category_info['description']}</p>
            </div>
        """
        for i, paper in enumerate(category_papers, 1):
            summary_html = ""
            if paper.summary:
                if isinstance(paper.summary, dict):
                    summary_html = render_structured_summary(paper.summary)
                else:
                    summary_html = f'<div class="llm-summary"><div class="summary-section">{markdown2.markdown(paper.summary)}</div></div>'
            else:
                summary_html = f'<p class="paper-abstract">{paper.abstract}</p>'
            authors_text = ', '.join(paper.authors[:3])
            if len(paper.authors) > 3:
                authors_text += f" et al. ({len(paper.authors)} authors)"
            content += f"""
            <div class="paper-card">
                <div class="paper-header">
                    <div class="paper-number">{i}</div>
                    <div class="paper-info">
                        <h3 class="paper-title">{paper.title}</h3>
                        <p class="paper-authors">By {authors_text}</p>
                        <div class="paper-meta">
                            <span class="category-badge">{paper.category}</span>
                            <span class="paper-date">{paper.published_data}</span>
                            {f'<span class="novelty-score">Novelty: {paper.novelty_score:.1f}</span>' if paper.novelty_score else ''}
                        </div>
                    </div>
                </div>
                <div class="paper-content">
                    {summary_html}
                    <div class="paper-actions">
                        <a href="https://arxiv.org/abs/{paper.arxiv_id}" class="btn btn-primary" target="_blank">
                            <i class="fas fa-external-link-alt"></i> Read Paper
                        </a>
                        <a href="https://arxiv.org/pdf/{paper.arxiv_id}" class="btn btn-outline-primary" target="_blank">
                            <i class="fas fa-file-pdf"></i> PDF
                        </a>
                    </div>
                </div>
            </div>
            """
        content += "</div>"
    content += """
    <div class="blog-footer">
        <p><em>This blog post was automatically generated from the latest AI research papers. Stay tuned for more updates!</em></p>
    </div>
    """
    return content

def get_category_info(category: str) -> Dict:
    """Get category-specific information for better presentation"""
    category_info = {
        "Generative AI & LLMs": {
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