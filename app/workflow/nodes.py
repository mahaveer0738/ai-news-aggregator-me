import os
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from app.workflow.state import WorkflowState, Article
from app.runner import run_scrapers
from app.services.process_youtube import process_youtube_transcripts
from app.database.repository import Repository
from app.tools.web_search import search_web_for_context
from app.tools.academic import search_wikipedia_for_background
import logging

logger = logging.getLogger(__name__)

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)

def scrape_news(state: WorkflowState) -> WorkflowState:
    """Node to scrape news and load it into the state."""
    logger.info("Scraping news...")
    hours = state.get("hours", 24)
    
    # Run existing scrapers (RSS & YouTube feed)
    run_scrapers(hours=hours)
    
    # Process YouTube Transcripts
    process_youtube_transcripts()
    
    # Load all unprocessed articles from DB for the time period
    repo = Repository()
    # We will fetch articles that don't have a digest yet
    unprocessed_youtube = repo.get_youtube_videos_without_transcript() # For simplicity, let's just get everything recent
    # To properly implement this, we should fetch from DB, but for the graph we can just use the state directly.
    # Let's fetch all recently added articles that need processing
    
    # Since we want to use the Graph, let's fetch raw data
    articles = []
    
    # Gather YouTube
    for v in repo.session.query(repo.models.YouTubeVideo).all():
        if not v.transcript: continue
        articles.append(Article(
            id=f"yt_{v.video_id}", title=v.title, url=v.url, source_type="youtube",
            raw_content=v.transcript, published_at=str(v.published_at)
        ))
    
    # Gather OpenAI
    for a in repo.session.query(repo.models.OpenAIArticle).all():
        articles.append(Article(
            id=f"oa_{a.id}", title=a.title, url=a.url, source_type="openai",
            raw_content=a.description, published_at=str(a.published_at)
        ))
        
    # Gather Anthropic
    for a in repo.session.query(repo.models.AnthropicArticle).all():
        articles.append(Article(
            id=f"an_{a.id}", title=a.title, url=a.url, source_type="anthropic",
            raw_content=a.description, published_at=str(a.published_at)
        ))
        
    # Limit to current batch just for the sake of the workflow
    state["articles"] = articles[:30] # Limit to 30 for processing speed
    return state

def enrich_news(state: WorkflowState) -> WorkflowState:
    """Node to enrich news articles using tools if they are too short."""
    logger.info("Enriching news...")
    for article in state["articles"]:
        if len(article.raw_content.split()) < 100:
            logger.info(f"Enriching article: {article.title}")
            try:
                # Use Web Search Tool to get more context
                extra_context = search_web_for_context.invoke(article.title)
                article.enriched_content = f"Original: {article.raw_content}\nWeb Context: {extra_context}"
            except Exception as e:
                logger.error(f"Failed to enrich: {e}")
                article.enriched_content = article.raw_content
        else:
            article.enriched_content = article.raw_content
    return state

def summarize_news(state: WorkflowState) -> WorkflowState:
    """Node to summarize the enriched news."""
    logger.info("Summarizing news...")
    
    prompt = PromptTemplate.from_template(
        "Summarize the following AI news article in 2-3 concise sentences.\n\n"
        "Title: {title}\n"
        "Content: {content}\n\n"
        "Summary:"
    )
    
    chain = prompt | llm
    
    for article in state["articles"]:
        try:
            content_to_use = article.enriched_content or article.raw_content
            res = chain.invoke({"title": article.title, "content": content_to_use[:3000]})
            article.summary = res.content
        except Exception as e:
            logger.error(f"Summary failed: {e}")
            article.summary = "Summary unavailable."
    
    return state

def rank_news(state: WorkflowState) -> WorkflowState:
    """Node to rank the summarized news."""
    logger.info("Ranking news...")
    
    prompt = PromptTemplate.from_template(
        "You are an expert AI curator. Evaluate the following news summary for its impact and relevance to AI engineers.\n"
        "Score it from 1 to 10 (10 being most important).\n\n"
        "Title: {title}\n"
        "Summary: {summary}\n\n"
        "Respond ONLY with a number."
    )
    
    chain = prompt | llm
    
    for article in state["articles"]:
        try:
            res = chain.invoke({"title": article.title, "summary": article.summary})
            score_str = res.content.strip()
            # Extract just the digits
            score = int(''.join(filter(str.isdigit, score_str)))
            article.relevance_score = min(10, max(1, score))
        except Exception:
            article.relevance_score = 5 # Default
            
    # Sort and rank
    sorted_articles = sorted(state["articles"], key=lambda x: x.relevance_score or 0, reverse=True)
    
    top_n = state.get("top_n", 10)
    state["articles"] = sorted_articles[:top_n]
    
    for i, a in enumerate(state["articles"]):
        a.rank = i + 1
        
    return state

def format_newsletter(state: WorkflowState) -> WorkflowState:
    """Node to format the newsletter."""
    logger.info("Formatting newsletter...")
    
    html = "<h1>Daily AI News Digest</h1><br/>"
    for a in state["articles"]:
        html += f"<h2>#{a.rank} - {a.title} (Score: {a.relevance_score}/10)</h2>"
        html += f"<p>{a.summary}</p>"
        html += f"<a href='{a.url}'>Read more</a><br/><br/>"
        
    state["email_html"] = html
    
    # Also add the processed articles to our RAG vectorstore!
    from app.rag.vectorstore import add_articles_to_vectorstore
    try:
        add_articles_to_vectorstore(state["articles"])
    except Exception as e:
        logger.error(f"Failed to add to vectorstore: {e}")
        
    return state

def send_newsletter(state: WorkflowState) -> WorkflowState:
    """Node to send the newsletter."""
    logger.info("Sending newsletter...")
    from app.services.process_email import send_email_via_resend
    
    email_html = state.get("email_html")
    if email_html:
        subject = "Your Daily AI Digest"
        recipient = os.getenv("MY_EMAIL", "test@example.com")
        success = send_email_via_resend(recipient, subject, email_html)
        state["delivery_status"] = "Success" if success else "Failed"
    else:
        state["delivery_status"] = "No content"
        
    return state
