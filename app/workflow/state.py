from typing import TypedDict, List, Dict, Any, Optional
import operator
from pydantic import BaseModel, Field

class Article(BaseModel):
    id: str
    title: str
    url: str
    source_type: str # "youtube", "openai", "anthropic"
    raw_content: str
    published_at: str
    enriched_content: Optional[str] = None
    summary: Optional[str] = None
    rank: Optional[int] = None
    relevance_score: Optional[int] = None
    reasoning: Optional[str] = None

class WorkflowState(TypedDict):
    """
    State representing the entire data pipeline through LangGraph.
    """
    # Number of hours to look back for news
    hours: int
    # Max number of top articles to include in the digest
    top_n: int
    
    # Articles fetched by scrapers
    articles: List[Article]
    
    # State tracking
    current_article_index: int
    
    # Final generated HTML newsletter
    email_html: Optional[str]
    
    # Delivery status
    delivery_status: str
