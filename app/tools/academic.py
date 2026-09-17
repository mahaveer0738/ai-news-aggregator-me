from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
from langchain_community.tools.arxiv.tool import ArxivQueryRun
from langchain_core.tools import tool

@tool
def search_wikipedia_for_background(query: str) -> str:
    """
    Search Wikipedia for background information on AI concepts, companies, or public figures
    mentioned in the news to provide better context in the newsletter.
    
    Args:
        query: Search term (e.g., 'Transformer neural network', 'Sam Altman')
    """
    api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=1000)
    tool = WikipediaQueryRun(api_wrapper=api_wrapper)
    try:
        return tool.run(query)
    except Exception as e:
        return f"Wikipedia error: {str(e)}"

@tool
def fetch_arxiv_paper_summary(query: str) -> str:
    """
    Search Arxiv for academic papers to summarize the latest AI research correctly.
    Use this when a news article mentions a specific research paper or breakthrough.
    
    Args:
        query: Paper title, author, or arxiv ID (e.g., 'Attention is all you need')
    """
    tool = ArxivQueryRun()
    try:
        return tool.run(query)
    except Exception as e:
        return f"Arxiv error: {str(e)}"
