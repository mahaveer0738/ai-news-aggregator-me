from langgraph.graph import StateGraph, START, END
from app.workflow.state import WorkflowState
from app.workflow.nodes import (
    scrape_news,
    enrich_news,
    summarize_news,
    rank_news,
    format_newsletter,
    send_newsletter
)

# Initialize the state graph
workflow = StateGraph(WorkflowState)

# Add all nodes
workflow.add_node("scraper", scrape_news)
workflow.add_node("enricher", enrich_news)
workflow.add_node("summarizer", summarize_news)
workflow.add_node("ranker", rank_news)
workflow.add_node("formatter", format_newsletter)
workflow.add_node("sender", send_newsletter)

# Add edges to define the pipeline execution flow
workflow.add_edge(START, "scraper")
workflow.add_edge("scraper", "enricher")
workflow.add_edge("enricher", "summarizer")
workflow.add_edge("summarizer", "ranker")
workflow.add_edge("ranker", "formatter")
workflow.add_edge("formatter", "sender")
workflow.add_edge("sender", END)

# Compile the graph
app_workflow = workflow.compile()

def run_workflow(hours: int = 24, top_n: int = 10):
    """Entry point to run the compiled LangGraph workflow."""
    initial_state = WorkflowState(
        hours=hours,
        top_n=top_n,
        articles=[],
        current_article_index=0,
        email_html=None,
        delivery_status="Pending"
    )
    
    # Run the graph
    result = app_workflow.invoke(initial_state)
    return result
