import os
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

def get_vectorstore():
    """Initializes and returns the Chroma VectorStore for the AI News Aggregator."""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Store the vector database in the local directory
    persist_directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "chroma_db")
    os.makedirs(persist_directory, exist_ok=True)
    
    vectorstore = Chroma(
        collection_name="ai_news",
        embedding_function=embeddings,
        persist_directory=persist_directory
    )
    return vectorstore

def add_articles_to_vectorstore(articles):
    """
    Adds a list of WorkflowState Articles to the vector store.
    """
    vectorstore = get_vectorstore()
    
    docs = []
    for article in articles:
        # Create a document with the summary as content and metadata
        doc = Document(
            page_content=f"Title: {article.title}\n\nSummary: {article.summary}",
            metadata={
                "id": article.id,
                "url": article.url,
                "source": article.source_type,
                "published_at": article.published_at,
                "rank": article.rank or 0
            }
        )
        docs.append(doc)
        
    if docs:
        vectorstore.add_documents(docs)
        print(f"Added {len(docs)} documents to ChromaDB.")
