# 🤖 AI News Aggregator

> A fully automated, AI-powered daily news digest pipeline that scrapes the latest AI content from YouTube, OpenAI, and Anthropic — summarizes it using Gemini, ranks it by your personal interests, and delivers a beautiful HTML email every day.

---

## 📌 Project Summary

**AI News Aggregator** is a Python-based pipeline that runs on a schedule (daily) to:

1. **Scrape** the latest AI content from curated YouTube channels (via RSS feeds), OpenAI's blog/RSS, and Anthropic's blog/RSS.
2. **Process** the raw content — fetch YouTube transcripts and parse Anthropic article markdown.
3. **Summarize** every article/video into a short, actionable digest using **Google Gemini 2.5 Flash**.
4. **Rank** the digests by relevance to your personal profile (interests, background, expertise) using a **Curator Agent** powered by Gemini with structured JSON output.
5. **Generate** a personalized email introduction using an **Email Agent**.
6. **Send** a beautifully formatted HTML email digest via the **Resend** email API.

Everything is stored in a **MySQL** database using **SQLAlchemy ORM**, making it easy to query, extend, and avoid re-processing already-seen content.

---

## 🗂️ Project Structure

```
ai-news-aggregator-me/
│
├── main.py                        # Entry point — runs the full pipeline
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variable template
├── create_tables.py               # Standalone script to create DB tables
│
├── app/
│   ├── config.py                  # YouTube channel IDs to scrape
│   ├── runner.py                  # Orchestrates all scrapers + saves to DB
│   ├── daily_runner.py            # Full 5-step pipeline with logging
│   │
│   ├── scrapers/
│   │   ├── youtube.py             # YouTube RSS + transcript scraper
│   │   ├── openai.py              # OpenAI RSS feed scraper
│   │   └── anthropic.py          # Anthropic RSS + markdown scraper
│   │
│   ├── agent/
│   │   ├── digest_agent.py        # Gemini agent: summarizes articles → digest
│   │   ├── curator_agent.py       # Gemini agent: ranks digests by user profile
│   │   └── email_agent.py         # Gemini agent: generates personalized intro
│   │
│   ├── services/
│   │   ├── process_anthropic.py   # Fetches & stores Anthropic markdown
│   │   ├── process_youtube.py     # Fetches & stores YouTube transcripts
│   │   ├── process_digest.py      # Calls DigestAgent for all unprocessed articles
│   │   ├── process_curator.py     # Calls CuratorAgent to rank digests
│   │   ├── process_email.py       # Assembles final email content
│   │   └── email.py               # Sends email via Resend API (HTML formatted)
│   │
│   ├── database/
│   │   ├── models.py              # SQLAlchemy ORM models
│   │   ├── connection.py          # DB engine/session setup
│   │   ├── repository.py          # All DB read/write operations
│   │   └── create_tables.py       # Creates tables from models
│   │
│   └── profiles/
│       └── user_profile.py        # Your personal interest profile for curation
│
├── docker/                        # (Reserved for Docker setup)
└── images/                        # Screenshots of the email output
```

---

## 🛠️ Tech Stack

### Language & Runtime
| Technology | Purpose |
|---|---|
| **Python 3.12+** | Core language for the entire pipeline |

### AI / LLM
| Technology | Purpose |
|---|---|
| **Google Gemini 2.5 Flash** (`google-genai`) | Powers all three AI agents — digest summarization, personalized curation/ranking, and email introduction generation |
| **Structured JSON Output** (Pydantic + Gemini) | Forces Gemini to return strongly-typed, validated JSON responses via `response_schema` |

### Web Scraping & Content Fetching
| Technology | Purpose |
|---|---|
| **feedparser** | Parses YouTube RSS feeds, OpenAI RSS, and Anthropic RSS to get latest articles |
| **requests** | HTTP client for fetching Anthropic article markdown content |
| **beautifulsoup4** (`bs4`) | HTML parsing for extracting clean article content |
| **lxml** | Fast XML/HTML parser used as the backend for BeautifulSoup |
| **youtube-transcript-api** | Fetches auto-generated or manual transcripts from YouTube videos |

### Database
| Technology | Purpose |
|---|---|
| **MySQL** | Relational database to persist all scraped articles, transcripts, and digests |
| **SQLAlchemy** | ORM layer for defining models and performing DB operations |
| **PyMySQL** | Pure Python MySQL driver used by SQLAlchemy |
| **mysql-connector-python** | Alternative MySQL connector for direct connections |

### Data Validation
| Technology | Purpose |
|---|---|
| **Pydantic v2** | Data models and validation for scraped content, AI agent outputs, and API responses |

### Email Delivery
| Technology | Purpose |
|---|---|
| **Resend** (`resend` Python SDK) | Transactional email API used to send the daily HTML digest email |
| **markdown** (Python library) | Converts Markdown-formatted digest summaries to clean HTML for the email |

### Configuration & Environment
| Technology | Purpose |
|---|---|
| **python-dotenv** | Loads environment variables from the `.env` file at runtime |

---

## 🤖 AI Agents

The project uses **three distinct Gemini-powered agents**, each with a focused role:

### 1. `DigestAgent` — Content Summarizer
- **Model:** `gemini-2.5-flash`
- **Role:** Takes a raw article title + content (up to 8,000 chars) and generates a concise **title + 2-3 sentence summary**
- **Output Schema:** `DigestOutput` (Pydantic model with `title` and `summary` fields)
- **Temperature:** `0.7` (creative but accurate)

### 2. `CuratorAgent` — Personalized Ranker
- **Model:** `gemini-2.5-flash`
- **Role:** Given a batch of digests and your **user profile**, ranks each article by relevance score (0–10) and assigns a rank position
- **Output Schema:** `RankedDigestList` → list of `RankedArticle` (score, rank, reasoning)
- **Temperature:** `0.3` (more deterministic for consistent ranking)
- **Personalization:** Uses your `USER_PROFILE` (name, background, interests, expertise level, preferences)

### 3. `EmailAgent` — Introduction Writer
- **Model:** `gemini-2.5-flash`
- **Role:** Generates a warm, personalized greeting and 2-3 sentence email introduction that previews the top-ranked articles
- **Output Schema:** `EmailIntroduction` (greeting + introduction)
- **Temperature:** `0.7`

---

## 🗄️ Database Schema

Four tables are managed via SQLAlchemy ORM:

| Table | Description |
|---|---|
| `youtube_videos` | Scraped YouTube videos with optional transcript text |
| `openai_articles` | Articles scraped from OpenAI's RSS feed |
| `anthropic_articles` | Articles scraped from Anthropic's RSS feed, with optional markdown |
| `digests` | AI-generated summaries linked to any article type |

---

## ⚙️ Pipeline Steps

The `run_daily_pipeline()` function in `daily_runner.py` orchestrates **5 sequential steps**:

```
[1/5] Scrape articles  →  YouTube RSS + OpenAI RSS + Anthropic RSS  →  Saved to MySQL
[2/5] Process Anthropic →  Fetch full markdown for Anthropic articles
[3/5] Process YouTube  →  Fetch transcripts for YouTube videos
[4/5] Create Digests   →  DigestAgent summarizes all unprocessed articles
[5/5] Send Email       →  CuratorAgent ranks → EmailAgent writes intro → Resend delivers
```

---

## 📦 Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/mahaveer0738/ai-news-aggregator-me.git
cd ai-news-aggregator-me
```

### 2. Create a virtual environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

```env
# Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Email (recipient address)
MY_EMAIL=your_email@example.com

# Resend API Key (https://resend.com)
RESEND_API_KEY=your_resend_api_key_here

# MySQL Database
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=ai_news_aggregator

# Optional: Webshare proxy for YouTube transcripts
PROXY_USERNAME=
PROXY_PASSWORD=
```

### 5. Create database tables
```bash
python create_tables.py
```

### 6. Customize your profile

Edit `app/profiles/user_profile.py` to match your interests:

```python
USER_PROFILE = {
    "name": "Your Name",
    "background": "Your background...",
    "interests": ["Generative AI", "LLMs", ...],
    "expertise_level": "Intermediate",  # Beginner / Intermediate / Advanced
    ...
}
```

### 7. Configure YouTube channels

Edit `app/config.py` to add/remove YouTube channel IDs:

```python
YOUTUBE_CHANNELS = [
    "UCn8ujwUInbJkBhffxqAPBVQ",  # Dave Ebbelaar
    "UCawZsQWqfGSbCI5yjkdVkTA",  # Matthew Berman
]
```

---

## 🚀 Running the Pipeline

### Run once (last 24 hours, top 10 articles)
```bash
python main.py
```

### Run with custom time window and article count
```bash
# Top 5 articles from the last 48 hours
python main.py 48 5
```

### Run individual steps
```bash
# Just the scrapers
python -m app.runner

# Just generate digests
python -m app.services.process_digest

# Just send the email
python -m app.services.process_email
```

---

## 📧 Email Output

The pipeline sends a styled HTML email containing:
- A personalized greeting with today's date
- A 2-3 sentence introduction highlighting the day's top themes
- Top-N ranked articles, each with:
  - An AI-generated title
  - A 2-3 sentence summary
  - A direct link to the original source

### Sample Output Screenshots

| Newsletter Overview | Top Articles |
|---|---|
| ![Newsletter Overview](images/newsletter-overview.png) | ![Top Articles](images/top-articles.png) |

---

## 📋 Requirements

```
google-genai          # Google Gemini API client
SQLAlchemy            # ORM for MySQL
pydantic              # Data validation and AI response schemas
python-dotenv         # Environment variable management
feedparser            # RSS feed parsing (YouTube, OpenAI, Anthropic)
youtube-transcript-api # YouTube transcript fetching
markdown              # Markdown → HTML conversion for emails
mysql-connector-python # MySQL connector
requests              # HTTP requests for fetching article content
beautifulsoup4        # HTML parsing
lxml                  # Fast XML/HTML parser
PyMySQL               # Pure Python MySQL driver
resend                # Transactional email delivery
```

---

## 🔑 API Keys Required

| Service | Where to Get |
|---|---|
| **Google Gemini** | [Google AI Studio](https://aistudio.google.com/apikey) |
| **Resend** | [resend.com](https://resend.com) |
| **MySQL** | Local install or any cloud MySQL provider (PlanetScale, Railway, etc.) |
| **Webshare Proxy** *(optional)* | [webshare.io](https://webshare.io) — only needed if YouTube transcript fetching is blocked |

---

## 👤 Author

**Mahaveer** — ECE Student & AI Developer  
B.Tech Electronics and Communication Engineering  
Interests: Generative AI, AI Agents, LLMs, RAG Systems, Python, Deep Learning

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

