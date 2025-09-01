# AI Research Papers Weekly

We summarize complex AI research papers into easy-to-read blogs for you! Get weekly curated summaries of breakthrough discoveries delivered straight to your inbox.

## Key Features

**Smart Paper Discovery**
- Automated arXiv fetching with intelligent relevance filtering
- Balanced paper selection across the last week
- Quality assessment based on novelty and relevance metrics

**Dynamic Blog Generation**
- Blogs are automatically generated every week with relevant fetched papers
- We show intiuitive and easy to understand summaries of each paper -> Generated using LLMs
- Category-based organization with visual navigation

**Advanced LLM Integration**
- Multi-provider support: Groq API (primary) + Ollama (fallback)
- Structured summaries with Problem, Innovation, Impact, and Analogy sections
- Robust error handling with exponential backoff

**Interactive Analytics**
- Paper clustering visualization
- Author analysis with H-index tracking
- Category scoring using cosine similarity

## Technology Stack

- **Backend**: Flask, SQLite with migrations
- **AI/ML**: Groq API, Ollama, Sentence Transformers
- **Frontend**: Bootstrap 5, JavaScript clustering visualization
- **Deployment**: Docker, Fly.io/Render ready

## Quick Start

1. **Install**
```bash
git clone https://github.com/yourusername/ai-research-papers-summarizer.git
cd ai-research-papers-summarizer
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

2. **Configure**
```bash
cp .env.example .env
# Add GROQ_API_KEY (optional but recommended)
```

3. **Choose LLM**
- **Groq API**: Get free key from console.groq.com
- **Ollama**: Run `ollama pull llama3 && ollama serve`

4. **Run**
```bash
python main.py
# Access at http://localhost:5000
```

## What Makes This Different

**Dynamic Content Generation**: Unlike static summarizers, blogs regenerate content when papers are updated, ensuring always-current insights.

**Intelligent Paper Distribution**: Automatically balances paper selection across time periods to avoid recency bias.

**Multi-LLM Resilience**: Seamless fallback between cloud (Groq) and local (Ollama) LLM providers for maximum reliability.

**Real-time Relationship Mapping**: Interactive visualization shows connections between papers and research trends.

## Project Structure

```
src/
├── web_app.py              # Flask application
├── arxiv_paper_fetcher.py  # Smart paper discovery
├── llm_summarizer.py       # Multi-provider LLM integration
├── database.py             # Database with migrations
├── blog.py                 # Dynamic content generation
└── paper_quality_filter.py # Quality assessment
```

## Deployment

**Docker**
```bash
docker build -t ai-research-daily . && docker run -p 5000:5000 ai-research-daily
```

**Cloud**
```bash
fly deploy  # or use render.yaml for Render
```

## License

MIT License