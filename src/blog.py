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
    grid_sections = [
        {
            "keys": ["key problem", "problem", "main problem", "challenge"],
            "icon": "🧩",
            "label": "Problem",
            "class": "problem-section"
        },
        {
            "keys": ["analogy", "intuitive explanation", "analogy / intuitive explanation"],
            "icon": "💡",
            "label": "Analogy",
            "class": "analogy-section"
        },
        {
            "keys": ["key innovation", "innovation", "novelty", "contribution"],
            "icon": "🚀",
            "label": "Key Innovation",
            "class": "innovation-section"
        },
        {
            "keys": ["practical impact", "impact", "real-world impact", "implications"],
            "icon": "🌍",
            "label": "Practical Impact",
            "class": "impact-section"
        }
    ]

    # Lowercase keys for matching
    summary_keys = {k.lower(): k for k in summary_dict.keys()}

    html = '<div class="llm-summary-grid-enhanced">'
    for section in grid_sections:
        section_content = ""
        found_key = None
        for key in section["keys"]:
            if key in summary_keys:
                found_key = summary_keys[key]
                section_content = summary_dict[found_key].strip()
                break
        
        if section_content:
            html += f'''
            <div class="summary-section-enhanced {section['class']}">
                <div class="section-header">
                    <h4 class="section-title">{section['label']}</h4>
                </div>
                <div class="section-content">
                    {markdown2.markdown(section_content)}
                </div>
            </div>'''
        else:
            # Show placeholder if no content found
            html += f'''
            <div class="summary-section-enhanced {section['class']} placeholder">
                <div class="section-header">
                    <h4 class="section-title">{section['label']}</h4>
                </div>
                <div class="section-content">
                    <p class="text-muted">Content not available</p>
                </div>
            </div>'''
    
    html += '</div>'
    return html

def get_category_anchor_id(category: str) -> str:
    """Generate anchor ID for category navigation"""

    category_anchors = {
        "Generative AI & LLMs": "generative-ai",
        "Computer Vision & MultiModal AI": "computer-vision",
        "Agentic AI": "agentic-ai",
        "AI in Healthcare": "healthcare-ai",
        "Explainable & Ethical AI": "explainable-ai"
    }
    return category_anchors.get(category, category.lower().replace(" ", "-").replace("&", "").replace("/", ""))

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
        anchor_id = get_category_anchor_id(category)
        content += f"""
        <div class="category-section id="{anchor_id}">
            <div class="category-header">
                <h2 class="category-title">{category}</h2>
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
            
            # Add institution tags if available
            institution_tags = ""
            if hasattr(paper, 'author_institutions') and paper.author_institutions:
                try:
                    if isinstance(paper.author_institutions, str):
                        institutions = eval(paper.author_institutions)
                    else:
                        institutions = paper.author_institutions
                    
                    if institutions and len(institutions) > 0:
                        # Get unique institutions and limit to top 3
                        unique_institutions = list(set([inst.strip() for inst in institutions if inst.strip()]))[:3]
                        if unique_institutions:
                            institution_tags = f"""
                            <div class="institution-tags mt-2">
                                <small class="text-dark">
                                    <i class="fas fa-university me-1"></i>
                                    {', '.join(unique_institutions)}
                                </small>
                            </div>"""
                except:
                    pass  # Skip if there's an error parsing institutions
            
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
                        </div>
                        {institution_tags}
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
                        <a href="/paper/{paper.arxiv_id}" 
                           class="btn btn-outline-primary">
                            <i class="fas fa-info-circle me-1"></i>
                            Details
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
            "description": "Breakthroughs in language models, text generation, and creative AI systems"
        },
        "Computer Vision & MultiModal AI": {
            "description": "Advances in image recognition, video analysis, and multimodal learning"
        },
        "Agentic AI": {
            "description": "Autonomous agents, multi-agent systems, and intelligent decision-making"
        },
        "AI in Healthcare": {
            "description": "AI applications in medical diagnosis, drug discovery, and healthcare systems"
        },
        "Explainable & Ethical AI": {
            "description": "Transparency, fairness, and responsible AI development"
        }
    }
    
    return category_info.get(category, {
        "description": "Cutting-edge research in artificial intelligence"
    })