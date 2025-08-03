"""
QA Chain initialization and management
"""

import streamlit as st
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from config.settings import OPENAI_API_KEY, QA_CHAIN_CONFIG

@st.cache_resource
def initialize_qa_chain():
    """Initialize the QA chain with caching"""
    try:
        embedding_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        
        vectorstore = FAISS.load_local(
            QA_CHAIN_CONFIG["vector_store_path"],
            embedding_model,
            allow_dangerous_deserialization=True
        )

        custom_prompt = PromptTemplate(
            input_variables=["context", "question", "chat_history"],
            template="""
        You are a friendly, casual mental health supporter. Talk like a caring friend - warm but not overly clinical.

        Keep responses:
        - Short and natural (1-3 sentences usually)  
        - Conversational, not formal
        - Focus on the person, not lengthy advice
        - Ask follow-up questions to keep dialogue flowing

        Context: {context}
        Chat history: {chat_history}
        Question: {question}

        Respond naturally and briefly:
        """
        )
        
        llm = OpenAI(
            temperature=QA_CHAIN_CONFIG["temperature"], 
            openai_api_key=OPENAI_API_KEY
        )
        
        memory = ConversationBufferMemory(
            memory_key="chat_history", 
            return_messages=True, 
            output_key="answer"
        )
        
        return ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(search_kwargs=QA_CHAIN_CONFIG["search_kwargs"]),
            memory=memory,
            return_source_documents=True,
            combine_docs_chain_kwargs={"prompt": custom_prompt}
        )
    
    except Exception as e:
        st.error(f"Failed to initialize QA chain: {e}")
        return None

def get_qa_response(qa_chain, question):
    """Get response from QA chain with error handling"""
    try:
        if qa_chain is None:
            return {"answer": "I'm sorry, but I'm having trouble accessing my knowledge base right now."}
        
        response = qa_chain.invoke({"question": question})
        return response
    except Exception as e:
        return {"answer": f"I encountered an error while processing your question: {e}"}