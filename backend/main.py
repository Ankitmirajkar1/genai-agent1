# =====================================================
# BACKEND/MAIN.PY - FastAPI Backend Server
# =====================================================
# REST API that exposes RAG functionality
# Frontend (Streamlit) calls these endpoints
#
# Endpoints:
# - GET  /health          - Check if API is alive
# - POST /ask             - Ask a question, get answer
# - GET  /                - API info
#
# Run: uv run python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

import sys
from pathlib import Path

# Add parent directory to path so we can import rag_core
sys.path.insert(0, str(Path(__file__).parent.parent))

# FastAPI imports
from fastapi import FastAPI, HTTPException  # FastAPI framework + error handling
from fastapi.middleware.cors import CORSMiddleware  # Allow cross-origin requests
from pydantic import BaseModel  # For request/response validation

# Import RAG system
from rag_core.simple_rag import rag

# =====================================================
# REQUEST/RESPONSE MODELS
# =====================================================
# These define what data the API expects and returns
# Pydantic validates the JSON automatically

class QuestionRequest(BaseModel):
    """Model for incoming requests (what frontend sends)"""
    question: str  # The question user is asking


class AnswerResponse(BaseModel):
    """Model for outgoing responses (what API sends back)"""
    question: str  # The original question
    answer: str  # The answer from RAG system
    sources: list  # List of source documents used


# =====================================================
# APP INITIALIZATION
# =====================================================
# Create FastAPI app
app = FastAPI(
    title="Rainbow Bazaar RAG API",
    description="API for answering questions about return/refund policy",
    version="1.0"
)

# Enable CORS - allows frontend to call backend API
# Without this, browser blocks cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (use specific domains in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# =====================================================
# STARTUP EVENT
# =====================================================
@app.on_event("startup")
async def startup_event():
    """
    Run when API starts
    Initialize RAG system: load or process PDF
    """
    print("\n" + "="*50)
    print("🚀 API STARTING UP")
    print("="*50)
    rag.setup()  # Load vector store or process PDF
    print("✅ API READY AT: http://localhost:8000")
    print("📚 API DOCS AT: http://localhost:8000/docs")
    print("="*50 + "\n")


# =====================================================
# ENDPOINTS
# =====================================================

@app.get("/health")
def health_check():
    """
    Health check endpoint
    Returns 200 OK if API is running
    Used by frontend to verify backend is online
    """
    return {"status": "✅ API is running"}


@app.get("/")
def root():
    """
    Root endpoint - shows API info
    """
    return {
        "name": "Rainbow Bazaar RAG API",
        "description": "Question-Answering system for Returns & Refunds Policy",
        "endpoints": {
            "health": "GET /health - Check if API is running",
            "ask": "POST /ask - Ask a question",
            "docs": "GET /docs - Interactive API documentation"
        }
    }


@app.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    """
    Main endpoint: Answer a question using RAG
    
    Input:
    {
        "question": "What is the return policy?"
    }
    
    Output:
    {
        "question": "What is the return policy?",
        "answer": "The return policy allows...",
        "sources": [{"page": 1, "source": "PDF name"}]
    }
    """
    # Validate: question must not be empty
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        # Call RAG system to get answer
        result = rag.ask(request.question)
        
        # Return formatted response
        return AnswerResponse(
            question=result["question"],
            answer=result["answer"],
            sources=result["sources"]
        )
    
    except Exception as e:
        # If error, return 500 with error message
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# =====================================================
# HOW TO RUN
# =====================================================
# Terminal 1:
#   cd d:\GenAI\Agentic AI\Project\RAG-Agent
#   uv run python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
#
# Then:
# - API: http://localhost:8000
# - Docs: http://localhost:8000/docs
