# RAG Chat App

A Retrieval-Augmented Generation (RAG) chat system with FastAPI backend and React frontend, supporting local documents (including Excel) and Azure OpenAI.

---

## Features

- Upload and index `.txt`, `.pdf`, `.md`, `.xls`, `.xlsx` files.
- FastAPI backend with RAG pipeline and code execution for data questions.
- React frontend with chat interface.
- Double-pass LLM review for more reliable answers.
- Table answers rendered as markdown tables.

---

## Prerequisite: Install Node.js

- Download and install Node.js (which includes npm) from [https://nodejs.org/](https://nodejs.org/).
- After installation, verify in your terminal:
    ```bash
    node -v
    npm -v
    ```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

### 2. Python Backend Setup

- Create and activate a virtual environment (optional but recommended):

    ```bash
    python -m venv .venv
    # On Windows:
    .venv\Scripts\activate
    # On macOS/Linux:
    source .venv/bin/activate
    ```

- Install backend dependencies:

    ```bash
    pip install -r requirements.txt
    ```

- **Set up Azure OpenAI environment variables** (replace with your actual values):

    ```powershell
    $env:AZURE_OPENAI_API_KEY="your-azure-openai-key"
    $env:AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"
    $env:AZURE_OPENAI_API_VERSION="2023-05-15"
    $env:AZURE_OPENAI_DEPLOYMENT_NAME="your-deployment-name"
    ```

- Prepare your documents:
    - Place `.txt`, `.pdf`, `.md`, `.xls`, `.xlsx` files in the [`docs`](docs) folder.

- Preprocess and index documents:

    ```bash
    python preprocess_docs.py
    ```

- Start the backend server:

    ```bash
    uvicorn backend:app --reload
    ```

---

### 3. React Frontend Setup

- Open a new terminal and go to the [`frontend`](frontend) folder:

    ```bash
    cd frontend
    ```

- Install frontend dependencies:

    ```bash
    npm install
    ```

- Start the frontend dev server:

    ```bash
    npm run dev
    ```

- Open your browser to the URL shown (usually [http://localhost:5173](http://localhost:5173)).

---

## Usage

- Ask questions about your documents in the chat interface.
- For data questions (e.g., filtering Excel), the agent will generate and execute code, returning the result as a table.
- The backend runs at [http://localhost:8000](http://localhost:8000) (API docs at `/docs`).

---

## Troubleshooting

- If you see CORS or network errors, ensure both backend and frontend are running.
- If you see `{"detail":"Not Found"}` at the backend root, visit `/` or `/docs` for a welcome message or API docs.
- If you update documents, re-run `python preprocess_docs.py` to refresh the index.

---

## Customization

- Adjust the prompt in [`backend.py`](backend.py) to change agent behavior.
- Add more document types or advanced logic as needed.
