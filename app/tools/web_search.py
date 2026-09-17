from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool

@tool
def search_web_for_context(query: str) -> str:
    """
    Search the web using DuckDuckGo to gather additional context or missing details 
    for AI news articles that are too short or lack depth.
    
    Args:
        query: The search query, e.g., 'OpenAI Sora release date details'
    """
    search = DuckDuckGoSearchRun()
    try:
        results = search.run(query)
        return results
    except Exception as e:
        return f"Error performing web search: {str(e)}"
