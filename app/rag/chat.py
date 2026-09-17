from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from app.rag.vectorstore import get_vectorstore

def get_rag_chain():
    """
    Creates and returns a Retrieval-Augmented Generation chain
    to answer questions about the AI news using the vectorstore.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    
    # Define prompt for Q&A
    system_prompt = (
        "You are an AI news assistant. Use the following pieces of retrieved context "
        "to answer the question. If you don't know the answer based on the context, "
        "just say that you don't know. Keep the answer concise and engaging.\n\n"
        "{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    
    return rag_chain

def chat_with_news(query: str) -> str:
    """Convenience function to chat with the news."""
    chain = get_rag_chain()
    response = chain.invoke({"input": query})
    return response["answer"]
