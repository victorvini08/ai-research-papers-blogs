# AI Research Papers Daily

A modern web application that automatically fetches, categorizes, and summarizes the latest AI research papers from arXiv. Stay updated with the most recent developments in artificial intelligence through daily blog summaries.

## Features

- **Automatic Paper Fetching**: Fetches latest AI research papers from arXiv
- **Smart Filtering**: Filters papers based on relevance to AI/ML topics
- **Daily Summaries**: Generates blog-style summaries of research papers
- **Beautiful UI**: Modern, responsive web interface
- **Paper Details**: Detailed view of individual research papers
- **Archive System**: Browse all historical daily summaries
- **Real-time Updates**: Manual and automatic paper fetching
- **Statistics**: Comprehensive analytics and insights

##  Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **APIs**: arXiv API
- **Styling**: Custom CSS with modern design principles

##  Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

##  Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-research-papers-summarizer
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (optional)
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your-secret-key-here
   FLASK_DEBUG=True
   DATABASE_PATH=database/papers.db
   ARXIV_MAX_RESULTS=50
   ```

##  Running the Application

1. **Start the web application**
   ```bash
   python main.py
   ```

2. **Open your browser**
   Navigate to `http://localhost:5000`

3. **Fetch your first papers**
   Click the "Fetch Papers" button in the navigation bar to get the latest AI research papers

## Usage

### Home Page
- View the latest daily summary
- Browse recent research papers
- Access quick actions to fetch papers or generate summaries

### Paper Details
- Click on any paper title to view detailed information
- Read abstracts and AI-generated summaries
- Access direct links to arXiv papers
- View paper metadata and statistics

### Archive
- Browse all historical daily summaries
- Search and filter summaries by date
- View statistics across all summaries

### API Endpoints
- `POST /api/fetch-papers`: Manually trigger paper fetching
- `POST /api/generate-summary`: Generate daily summary for a specific date

##  Project Structure

```
ai-research-papers-summarizer/
├── src/
│   ├── __init__.py
│   ├── web_app.py          # Flask web application
│   ├── paper_fetcher.py    # arXiv paper fetching logic
│   ├── database.py         # Database operations
│   ├── categorizer.py      # Paper categorization (future)
│   └── summarizer.py       # AI summarization (future)
├── templates/              # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── paper_detail.html
│   ├── daily_summary.html
│   ├── archive.html
│   └── 404.html
├── static/                 # Static assets (CSS, JS, images)
├── database/              # SQLite database files
├── main.py                # Application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Configuration

The application can be configured through environment variables or by modifying `config.py`:

- `SECRET_KEY`: Flask secret key for session management
- `DATABASE_PATH`: Path to SQLite database file
- `ARXIV_MAX_RESULTS`: Maximum number of papers to fetch from arXiv
- `MAX_PAPERS_PER_SUMMARY`: Maximum papers to include in daily summaries
- `PAPERS_PER_PAGE`: Number of papers to display per page

## Database Schema

### Papers Table
- `id`: Primary key
- `arxiv_id`: arXiv identifier
- `title`: Paper title
- `authors`: JSON array of authors
- `abstract`: Paper abstract
- `categories`: JSON array of arXiv categories
- `published_date`: Publication date
- `summary`: AI-generated summary (future)
- `category`: Assigned category (future)
- `novelty_score`: Novelty score (future)

### Daily Summaries Table
- `id`: Primary key
- `date`: Summary date
- `summary_content`: Generated summary content
- `paper_count`: Number of papers in summary
- `created_at`: Creation timestamp

## Future Enhancements

- **AI Summarization**: Integrate OpenAI GPT or similar for paper summarization
- **Paper Categorization**: Automatic categorization of papers by topic
- **Novelty Scoring**: AI-powered novelty assessment
- **Email Notifications**: Daily digest emails
- **RSS Feeds**: RSS feed for daily summaries
- **Advanced Filtering**: Filter by authors, institutions, topics
- **Paper Recommendations**: Personalized paper recommendations
- **Social Features**: Comments, likes, sharing
- **Mobile App**: Native mobile application

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- arXiv.org for providing the research paper data
- The AI research community for their valuable contributions
- Bootstrap and Font Awesome for the beautiful UI components

## Support

If you have any questions or need help, please open an issue on GitHub or contact the maintainers.

---

**Happy exploring the latest AI research!
