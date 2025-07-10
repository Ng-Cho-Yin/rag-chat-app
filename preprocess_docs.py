import os
import pandas as pd
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
import markdown

DOCS_DIR = "docs"
INDEX_PATH = "faiss_index"

all_docs = []
for filename in os.listdir(DOCS_DIR):
    file_path = os.path.join(DOCS_DIR, filename)
    ext = filename.split(".")[-1].lower()
    if ext == "txt":
        loader = TextLoader(file_path)
        docs = loader.load()
    elif ext == "pdf":
        loader = PyPDFLoader(file_path)
        docs = loader.load()
    elif ext == "md":
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        plain_text = ''.join(markdown.markdown(text).split('<')[::2])
        docs = [Document(page_content=plain_text)]
    elif ext in ["xls", "xlsx"]:
        df = pd.read_excel(file_path)
        docs = [Document(page_content=df.to_csv(index=False))]
    else:
        continue
    all_docs.extend(docs)

splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=100)
splits = splitter.split_documents(all_docs)

embeddings = HuggingFaceEmbeddings()
vectorstore = FAISS.from_documents(splits, embeddings)
vectorstore.save_local(INDEX_PATH)

print(f"Indexed {len(splits)} document chunks. Index saved to {INDEX_PATH}/")
