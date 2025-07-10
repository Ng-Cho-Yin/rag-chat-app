import os
import re
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
from langchain.chains import RetrievalQA

INDEX_PATH = "faiss_index"

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vectorstore = FAISS.load_local(INDEX_PATH, HuggingFaceEmbeddings(), allow_dangerous_deserialization=True)
retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 8})

custom_prompt = PromptTemplate(
    template="""
    You are a helpful assistant. If the user's question is about data filtering, transformation, or aggregation, first generate the appropriate SQL or pandas command to answer the question, then use the context to answer. If the context contains tabular data (CSV), you may use pandas-like logic to process it. Otherwise, answer as usual.

    Context:
    {context}

    Question: {question}
    Answer:
    """,
    input_variables=["context", "question"]
)

class ChatRequest(BaseModel):
    message: str
    history: list = []

# Load all Excel files into a dict of DataFrames for code execution
excel_dfs = {}
for filename in os.listdir("docs"):
    if filename.lower().endswith((".xls", ".xlsx")):
        excel_dfs[filename] = pd.read_excel(os.path.join("docs", filename))

@app.post("/chat")
async def chat(req: ChatRequest):
    llm = AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        temperature=0.0
    )
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type_kwargs={"prompt": custom_prompt}
    )
    result = qa.invoke({"query": req.message})
    answer = result["result"]

    # Double-pass: Ask LLM to review and improve its own answer
    try:
        review_prompt = f"请检查并改进以下回答，确保其准确、简明且无遗漏：\n{answer}\n如果有代码或表格，请确保其正确且仅保留最终用户友好的答案。"
        improved_answer = llm.invoke(review_prompt)
        # Handle possible dict or object return
        if isinstance(improved_answer, dict):
            # Try common keys
            answer = improved_answer.get("content") or improved_answer.get("text") or str(improved_answer)
        elif hasattr(improved_answer, "content"):
            answer = improved_answer.content
        else:
            answer = str(improved_answer)
    except Exception as e:
        answer = str(answer)  # Fallback to original answer if review step fails

    pandas_result = None
    # Try to extract and execute pandas code
    import re
    code_match = re.search(r'```python(.*?)```', answer, re.DOTALL)
    executed = False
    if code_match:
        code = code_match.group(1).strip()
        for fname, df in excel_dfs.items():
            local_vars = {"data": df}
            try:
                code_clean = re.sub(r'pd\.read_(csv|excel)\([^)]+\)', 'data', code)
                exec(code_clean, {"pd": pd}, local_vars)
                filtered = None
                for v in reversed(list(local_vars.values())):
                    if isinstance(v, pd.DataFrame):
                        filtered = v
                        break
                if filtered is not None and not filtered.empty:
                    answer = filtered.to_markdown(index=False)
                    executed = True
                    break
            except Exception:
                continue
    # If no pandas code, but SQL is present, ask LLM to convert SQL to pandas and execute
    if not executed:
        sql_match = re.search(r'```sql(.*?)```', answer, re.DOTALL)
        if sql_match:
            sql_code = sql_match.group(1).strip()
            # Ask LLM to convert SQL to pandas code
            followup_prompt = f"请将以下SQL查询转换为pandas代码，假设DataFrame变量名为data：\n{sql_code}"
            pandas_code = llm.invoke(followup_prompt)
            code_match2 = re.search(r'```python(.*?)```', pandas_code, re.DOTALL)
            if code_match2:
                code2 = code_match2.group(1).strip()
                for fname, df in excel_dfs.items():
                    local_vars = {"data": df}
                    try:
                        code_clean2 = re.sub(r'pd\.read_(csv|excel)\([^)]+\)', 'data', code2)
                        exec(code_clean2, {"pd": pd}, local_vars)
                        filtered = None
                        for v in reversed(list(local_vars.values())):
                            if isinstance(v, pd.DataFrame):
                                filtered = v
                                break
                        if filtered is not None and not filtered.empty:
                            answer = filtered.to_markdown(index=False)
                            executed = True
                            break
                    except Exception:
                        continue
    # If still not executed, just return the original answer (text)
    # Always return only the part after 'Answer:' if present, with error handling
    try:
        answer_str = str(answer) if answer is not None else ""
        # If the answer looks like a markdown table, return as a table
        if answer_str.strip().startswith("|") and "|" in answer_str.strip():
            return {"answer": answer_str, "type": "table"}
        answer_match = re.search(r'Answer:\s*(.*)', answer_str, re.DOTALL)
        if answer_match:
            answer_clean = answer_match.group(1).strip()
        else:
            answer_clean = answer_str.strip()
    except Exception as e:
        print(f"Post-processing error: {e}")
        answer_clean = "很抱歉，未能生成清晰的答案。请重试或检查数据格式。"
    return {"answer": str(answer_clean), "type": "text"}

@app.get("/")
def root():
    return {"message": "Backend is running. Use the /chat endpoint for API requests."}
