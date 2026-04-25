# 🛍️ Rainbow Bazaar RAG - Simple Setup

This is a VERY SIMPLE RAG application for answering questions about the Rainbow Bazaar Returns Policy PDF.

## 📁 Files Structure

```
RAG-Agent/
├── config.py              # Configuration (API keys, paths)
├── simple_rag.py          # RAG logic (very simple!)
├── backend_api.py         # FastAPI backend
├── frontend/
│   └── app.py            # Streamlit frontend
├── data/
│   ├── Rainbow-Bazaar-Return-Refund-&-Cancellation-Policy.pdf
│   └── vector_store/     # Auto-created on first run
├── pyproject.toml        # UV dependencies
├── start_backend.bat     # Windows batch file
├── start_frontend.bat    # Windows batch file
└── .env                  # Your API keys (already configured)
```

##  Quick Start

### Step 1: Install Dependencies (ONE TIME)
```bash
uv sync
```

### Step 2: Start Backend API (Terminal 1)
```bash
cd "RAG-Agent"
uv run python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
 API READY AT: http://localhost:8000
 API DOCS AT: http://localhost:8000/docs
```

### Step 3: Start Frontend (Terminal 2)
```
cd "RAG-Agent"
uv run streamlit run frontend/app.py
```

You should see:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

### Step 4: Open Browser
Go to: **http://localhost:8501**

##  How It Works

1. **First Run**: The backend processes the PDF and creates a vector store (1-2 minutes)
2. **Subsequent Runs**: Uses cached vector store (instant)
3. **User asks question** → Streamlit sends to API → API searches PDF → LLM answers
4. **Answer + sources** displayed in Streamlit

## 🎯 What Each File Does

| File | Purpose |
|------|---------|
| `config.py` | Loads API keys and paths |
| `simple_rag.py` | RAG logic: loads PDF, creates embeddings, does searches |
| `backend_api.py` | FastAPI server with `/ask` endpoint |
| `frontend/app.py` | Streamlit UI for asking questions |

##  Code Explanation

### simple_rag.py
- `SimpleRAG class` - Main RAG logic
- `setup()` - Initialize and load/create vector store
- `ask(question)` - Query the system and return answer + sources

### backend_api.py
- `@app.on_event("startup")` - Initialize RAG when server starts
- `@app.post("/ask")` - Accept questions and return answers
- Uses the `simple_rag` module

### frontend/app.py
- Text input for questions
- Button to submit
- Display answer and sources
- Health check to verify API is running

##  Troubleshooting

**API won't start:**
- Check .env file has OPENAI_API_KEY
- Check port 8000 is not in use: `netstat -ano | findstr :8000`

**Streamlit can't connect to API:**
- Make sure backend is running first
- Check http://localhost:8000/health in browser

**PDF processing is slow:**
- First run takes 1-2 minutes (normal)
- Uses OpenAI embeddings API
- Cached after first run

**How to clear cache and reprocess PDF:**
- Delete `data/vector_store/` folder
- Run backend again - will reprocess PDF

##  Environment Variables (Already in .env)
- `OPENAI_API_KEY` - For embeddings and answers
- `OPENAI_MODEL` - Which model to use (gpt-4.1)
- `LANGCHAIN_API_KEY` - For tracing (optional)

##  Windows Batch Files

Instead of typing commands, you can use batch files:

1. **start_backend.bat** - Double-click to start backend
2. **start_frontend.bat** - Double-click to start frontend

##  API Documentation

When backend is running, visit: http://localhost:8000/docs

This shows all endpoints:
- `GET /health` - Check if API is running
- `POST /ask` - Ask a question

##  Done!

That's it! Very simple RAG system that just works.

Questions → PDF Search → LLM Answer → Display Result

Enjoy! 
