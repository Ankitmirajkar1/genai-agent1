# =====================================================
# CONFIG.PY - Configuration & Environment Variables
# =====================================================
# This file loads all settings: API keys, paths, credentials
# Load once at startup, use everywhere

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file (contains OPENAI_API_KEY, etc.)
load_dotenv()

# =====================================================
# API KEYS (from .env file)
# =====================================================
# OpenAI API key - for creating embeddings and answering questions
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Which OpenAI model to use (e.g., gpt-4, gpt-3.5-turbo)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

# LangChain API key - for tracing/monitoring (optional)
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

# =====================================================
# FILE PATHS
# =====================================================
# Get the project root directory (where this file is located)
BASE_DIR = Path(__file__).parent

# Path to the PDF document we're asking questions about
PDF_PATH = BASE_DIR / "data" / "Rainbow-Bazaar-Return-Refund-&-Cancellation-Policy.pdf"

# Path where we save the vector store (cached embeddings for speed)
VECTOR_STORE_PATH = BASE_DIR / "data" / "vector_store"

# =====================================================
# VALIDATION & SETUP
# =====================================================
# Create directories if they don't exist
PDF_PATH.parent.mkdir(parents=True, exist_ok=True)
VECTOR_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)

# Print confirmation that config loaded
print(f"✅ Config loaded: PDF at {PDF_PATH}")
print(f"✅ Vector store will be at {VECTOR_STORE_PATH}")
