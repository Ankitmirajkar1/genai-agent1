# =====================================================
# DOCKERFILE - Build Docker image for RAG App
# =====================================================

# Start from official Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy all project files into container
COPY . /app

# Install uv package manager (faster than pip)
RUN pip install uv

# Install all Python dependencies from pyproject.toml using uv
RUN uv sync --frozen

# =====================================================
# EXPOSE PORTS
# =====================================================
# Port 8000: Backend API (FastAPI)
EXPOSE 8000

# Port 8501: Frontend (Streamlit)
EXPOSE 8501

# =====================================================
# ENVIRONMENT SETUP
# =====================================================
# Load environment variables from .env file
ENV PYTHONUNBUFFERED=1

# =====================================================
# RUN BOTH SERVICES
# =====================================================
# Start both backend and frontend using shell script
# Backend runs in background, frontend runs in foreground
CMD ["sh", "-c", "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &  streamlit run frontend/app.py --server.port=8501 --server.address=0.0.0.0"]