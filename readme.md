# 🤖 AI News Aggregator v2

> A fully automated, production-ready AI-powered daily news digest pipeline that scrapes the latest AI content, enriches it via the web, summarizes and ranks it using Gemini, and provides an interactive RAG Chat interface. Now powered by **LangGraph**, **FastAPI**, and **ChromaDB**!

---

## 📌 Project Summary

**AI News Aggregator v2** is a Multi-Agent System that operates as a robust web service to:

1. **Scrape** the latest AI content from curated YouTube channels (via RSS feeds), OpenAI's blog, and Anthropic's blog.
2. **Enrich** the raw content using a **Researcher Agent** that queries DuckDuckGo, Wikipedia, and Arxiv for missing context.
3. **Summarize** every article/video into a short, actionable digest using a **Writer Agent** (Google Gemini 2.5 Flash).
4. **Rank** the digests by relevance to your personal profile using a **Curator Agent**.
5. **Format & Send** a beautifully formatted HTML email digest.
6. **Store & Chat** with the news! Every article is embedded into a local **ChromaDB** Vector Database, allowing you to ask questions via a Conversational Retrieval-Augmented Generation (RAG) API.

Everything is exposed through a **FastAPI** backend, making it easy to integrate with a frontend UI or mobile app!

---

## 🗂️ Project Structure

```
ai-news-aggregator-me/
│
├── main.py                        # Entry point — starts the FastAPI server
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variable template
├── create_tables.py               # Script to create MySQL DB tables
│
├── app/
│   ├── api/
│   │   └── main.py                # FastAPI routes (/trigger-pipeline, /chat, etc.)
│   │
│   ├── workflow/
│   │   ├── graph.py               # LangGraph StateGraph definition
│   │   ├── nodes.py               # LangGraph agent nodes (Scrape, Enrich, Summarize, Rank, Format, Send)
│   │   └── state.py               # LangGraph state schema (WorkflowState)
│   │
│   ├── rag/
│   │   ├── chat.py                # LangChain Conversational Retrieval Chain
│   │   └── vectorstore.py         # ChromaDB initialization and indexing
│   │
│   ├── tools/
│   │   ├── web_search.py          # DuckDuckGo search tool
│   │   └── academic.py            # Wikipedia & Arxiv search tools
│   │
│   ├── config.py                  # YouTube channel IDs to scrape
│   ├── runner.py                  # Scraper orchestration
│   ├── daily_runner.py            # Legacy pipeline (optional)
│   │
│   ├── scrapers/                  # YouTube, OpenAI, Anthropic scraper implementations
│   ├── agent/                     # Legacy Gemini agent definitions
│   ├── services/                  # Business logic (DB read/writes, Resend email logic)
│   ├── database/                  # SQLAlchemy models and connection
│   └── profiles/                  # User personal interest profiles
│
└── data/
    └── chroma_db/                 # Local directory for ChromaDB vector embeddings
```

---

## 🛠️ Tech Stack

### Frameworks & Libraries
- **FastAPI**: High-performance API backend.
- **LangGraph**: Stateful, multi-agent orchestrator for the news pipeline.
- **LangChain**: Abstraction layer for LLMs, Tools, and RAG.
- **ChromaDB**: Local vector database for semantic search and embeddings.

### AI / LLM
- **Google Gemini 2.5 Flash** (`langchain-google-genai`): Powers the agents and conversational RAG.
- **Google Generative AI Embeddings**: Used to embed articles into ChromaDB.

### Web Scraping & Tools
- **DuckDuckGo Search API**: Real-time web search for context enrichment.
- **Wikipedia & Arxiv APIs**: Academic and background research tools.
- **feedparser**, **youtube-transcript-api**, **beautifulsoup4**: For scraping raw sources.

### Database
- **MySQL / SQLAlchemy**: Relational database to persist raw scraped articles.
- **ChromaDB**: Vector storage for processed summaries.

### Email Delivery
- **Resend**: Transactional email API for HTML digests.

---

## 🤖 Multi-Agent LangGraph Pipeline

The project uses a powerful **LangGraph StateGraph** to manage data flow between agents:

1. **Scraper Node**: Fetches raw data from MySQL.
2. **Enricher Node (Researcher)**: Evaluates if an article is too short. If so, uses DuckDuckGo/Wikipedia to pull missing context.
3. **Summarizer Node (Writer)**: Takes enriched context and outputs a clean 2-3 sentence summary.
4. **Ranker Node (Curator)**: Scores relevance from 1-10.
5. **Formatter Node**: Generates HTML and saves the final summaries as embeddings into ChromaDB.
6. **Sender Node**: Delivers the email via Resend.

---

## 📦 Installation & Setup

### 1. Clone & Setup Virtual Environment
```bash
git clone https://github.com/mahaveer0738/ai-news-aggregator-me.git
cd ai-news-aggregator-me
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env` and fill in:
```env
GEMINI_API_KEY=your_gemini_api_key_here
MY_EMAIL=your_email@example.com
RESEND_API_KEY=your_resend_api_key_here

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=ai_news_aggregator
```

### 4. Initialize MySQL Tables
```bash
python create_tables.py
```

---

## 🚀 Running the API Server

Start the FastAPI server via Uvicorn:
```bash
python main.py
```
*(Runs on `http://0.0.0.0:8000` by default)*

### API Endpoints:

1. **Trigger Pipeline (POST `/trigger-pipeline`)**
   - Automatically kicks off the LangGraph background job to scrape, enrich, summarize, and email.
   - Request Body: `{"hours": 24, "top_n": 10}`

2. **Chat with News (POST `/chat`)**
   - Query your ChromaDB instance using RAG!
   - Request Body: `{"query": "What did OpenAI announce this week?"}`

Visit `http://localhost:8000/docs` to interact directly with the Swagger UI!

---

## 👤 Author

**Mahaveer** — ECE Student & AI Developer  
B.Tech Electronics and Communication Engineering  
Interests: Generative AI, AI Agents, LLMs, RAG Systems, Python, Deep Learning

---

## 📄 License
This project is open source and available under the [MIT License](LICENSE).
