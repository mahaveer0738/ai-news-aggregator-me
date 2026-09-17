from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

from app.workflow.graph import run_workflow
from app.rag.chat import chat_with_news

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI News Aggregator API",
    description="Production-ready API for the AI News Aggregator with LangGraph and RAG capabilities.",
    version="1.0.0"
)

class PipelineRunRequest(BaseModel):
    hours: int = 24
    top_n: int = 10

class ChatRequest(BaseModel):
    query: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI News Aggregator API!"}

@app.post("/trigger-pipeline")
def trigger_pipeline(request: PipelineRunRequest, background_tasks: BackgroundTasks):
    """
    Triggers the LangGraph pipeline in the background to scrape, enrich, summarize, rank, and email news.
    """
    background_tasks.add_task(run_workflow, request.hours, request.top_n)
    return {"message": f"Pipeline triggered in background for the last {request.hours} hours."}

@app.post("/chat")
def chat(request: ChatRequest):
    """
    Chat with the AI News database using RAG.
    """
    try:
        answer = chat_with_news(request.query)
        return {"query": request.query, "answer": answer}
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat query.")
