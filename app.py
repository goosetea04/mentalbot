import streamlit as st
from dotenv import load_dotenv
import os

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# Load environment variables
load_dotenv()

# Initialize embedding model
embedding_model = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

# Load FAISS vector store
vectorstore = FAISS.load_local(
    "mental_health_index",
    embedding_model,
    allow_dangerous_deserialization=True
)

# Create LLM
llm = OpenAI(
    temperature=0.5,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Memory (set return_messages=True so LangChain can format chat properly)
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="answer"  # ✅ This is the key fix
)

# Conversational Retrieval Chain
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    memory=memory,
    return_source_documents=True
)

# Streamlit UI
st.title("Mental Health First Aid Chatbot")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("You:")

if user_input:
    try:
        response = qa_chain.invoke({"question": user_input})
        answer = response["answer"]
        sources = response.get("source_documents", [])

        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("Bot", answer, sources))

    except Exception as e:
        st.error(f"An error occurred: {e}")

# Display history with sources
for entry in st.session_state.chat_history:
    if entry[0] == "You":
        st.write(f"**You:** {entry[1]}")
    else:
        bot_response, source_docs = entry[1], entry[2]
        st.write(f"**Bot:** {bot_response}")
        if source_docs:
            with st.expander("Source Pages"):
                for doc in source_docs:
                    page = doc.metadata.get("page", "Unknown")
                    st.markdown(f"- Page **{page + 1}**: {doc.page_content[:200]}...")
