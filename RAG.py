# RAG.py
# This script will use LangChain for Retrieval-Augmented Generation (RAG) workflows.

import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import os
from langchain.prompts import PromptTemplate
import matplotlib.pyplot as plt
import io
import base64

INDEX_PATH = "faiss_index"

# Load FAISS index
if not os.path.exists(INDEX_PATH):
    st.error("No FAISS index found. Please run preprocess_docs.py first.")
    st.stop()

vectorstore = FAISS.load_local(INDEX_PATH, HuggingFaceEmbeddings(), allow_dangerous_deserialization=True)
retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 8})

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

st.title("Local Document RAG Demo (Preprocessed)")
user_query = st.text_input("Ask a question about your documents:")

# Display chat history
for entry in st.session_state.chat_history:
    st.markdown(f"**You:** {entry['user']}")
    st.markdown(f"**Agent:** {entry['agent']}")

custom_prompt = PromptTemplate(
    template="""
    You are a helpful assistant. Use the following context to answer the user's question as comprehensively as possible. If the question asks for a list or all people, make sure to include everyone mentioned in the context. If you don't know, say you don't know.

    Context:
    {context}

    Question: {question}
    Answer:
    """,
    input_variables=["context", "question"]
)

if user_query:
    from langchain_openai import AzureChatOpenAI
    from langchain.chains import RetrievalQA
    llm = AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION")
    )
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type_kwargs={"prompt": custom_prompt}
    )
    result = qa.invoke({"query": user_query})
    st.write("**Answer:**", result["result"])

    # Add to chat history
    st.session_state.chat_history.append({"user": user_query, "agent": result["result"]})

    # Try to generate a graph if the answer contains data
    if "|" in result["result"] and result["result"].count("\n") > 1:
        # Try to parse as markdown table
        import pandas as pd
        from io import StringIO
        try:
            df = pd.read_csv(StringIO(result["result"]), sep="|").dropna(axis=1, how="all")
            if len(df.columns) > 1:
                st.write("### Relevant Graph:")
                fig, ax = plt.subplots()
                df.plot(ax=ax, kind="bar")
                st.pyplot(fig)
        except Exception as e:
            st.info("No graphable data found in the answer.")
else:
    st.info("Enter a question to query your preprocessed documents.")
