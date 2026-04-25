# =====================================================
# SIMPLE_RAG.PY - Core RAG (Retrieval Augmented Generation) Logic
# =====================================================
# RAG = Load PDF → Create Embeddings → Store Vectors → Answer Questions
# 
# How it works:
# 1. Load PDF document
# 2. Split text into chunks
# 3. Convert chunks to vectors (embeddings)
# 4. Store in FAISS (vector database)
# 5. When user asks: find relevant chunks + ask LLM to answer
#
# This makes LLM aware of YOUR specific document

import os
import sys
from pathlib import Path

# Add parent directory to path so we can import config
sys.path.insert(0, str(Path(__file__).parent.parent))

# LangChain imports - library for building AI apps
from langchain_community.document_loaders import PyPDFLoader  # Load PDF files
from langchain_text_splitters import RecursiveCharacterTextSplitter  # Split text smartly
from langchain_community.vectorstores import FAISS  # Vector database (search by similarity)
from langchain_openai import OpenAIEmbeddings, ChatOpenAI  # OpenAI embeddings + LLM

# Import configuration (API keys, paths)
from config import PDF_PATH, VECTOR_STORE_PATH, OPENAI_API_KEY, OPENAI_MODEL


class SimpleRAG:
    """
    Simple RAG class - handles everything for question answering
    
    Main methods:
    - __init__(): Initialize embeddings and LLM
    - setup(): Load or create vector store
    - process_pdf(): Load PDF and create embeddings
    - load_vector_store(): Load cached embeddings
    - ask(): Answer a question using RAG
    """
    
    def __init__(self):
        # Initialize embeddings
        print("📦 Initializing embeddings...")
        
        # Create embeddings object - converts text to vectors using OpenAI
        # Vectors are used to find similar text chunks
        self.embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
        
        # Will store the vector database (FAISS)
        self.vector_store = None
        
        # Create LLM object - will answer questions
        # temperature=0.7: medium creativity (0=consistent, 1=creative)
        self.llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model=OPENAI_MODEL,
            temperature=0.7
        )
        
    def setup(self):
        """Setup RAG - either load existing vector store or create new one"""
        print("\n🚀 Setting up RAG system...")
        
        # Check if we already processed the PDF before
        if Path(VECTOR_STORE_PATH).exists():
            # Yes - just load the cached vector store
            print("📂 Loading existing vector store...")
            self.load_vector_store()
        else:
            # No - process PDF for the first time
            print("📄 Processing PDF for first time (this takes a minute)...")
            self.process_pdf()
        
        print("✅ RAG Ready!\n")
    
    def process_pdf(self):
        """
        Process PDF and create vector store
        Steps: Load → Split → Embed → Store
        """
        # Step 1: Load PDF document
        print(f"  Loading: {PDF_PATH}")
        loader = PyPDFLoader(str(PDF_PATH))
        documents = loader.load()  # Load all pages
        print(f"  ✓ Loaded {len(documents)} pages")
        
        # Step 2: Split document into smaller chunks
        # Why chunks? LLM has token limits. Also helps find relevant parts faster
        print("  Splitting into chunks...")
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,  # Each chunk ~500 characters
            chunk_overlap=100,  # 100 char overlap keeps context between chunks
        )
        chunks = splitter.split_documents(documents)
        print(f"  ✓ Created {len(chunks)} chunks")
        
        # Step 3: Create embeddings (vectors) from chunks and store in FAISS
        # This takes time because it calls OpenAI API for each chunk
        print("  Creating vector store (this may take 1-2 minutes)...")
        self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        
        # Step 4: Save to disk for next time (don't need to reprocess)
        self.vector_store.save_local(str(VECTOR_STORE_PATH))
        print(f"  ✓ Saved to {VECTOR_STORE_PATH}")
    
    def load_vector_store(self):
        """Load pre-computed vector store from disk (fast!)"""
        self.vector_store = FAISS.load_local(
            str(VECTOR_STORE_PATH),
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        print("  ✓ Vector store loaded")
    
    def ask(self, question: str):
        """
        Answer a question using RAG
        
        Process:
        1. Search vector store for top 3 similar chunks
        2. Combine chunks as context
        3. Send to LLM with context + question
        4. Get answer + return sources
        """
        if self.vector_store is None:
            return {"error": "RAG not initialized"}
        
        # Step 1: Search for top 3 most relevant chunks (similarity search)
        # Returns chunks with highest vector similarity to the question
        docs = self.vector_store.similarity_search(question, k=3)
        
        # Step 2: Combine all relevant chunks into one context string
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Step 3: Create prompt for LLM with context + question
        # This tells LLM to use the context to answer
        prompt = f"""You are a helpful assistant answering questions about Rainbow Bazaar's Return and Refund Policy.

Use the context provided to answer the question. If you don't know, say you don't know.

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""
        
        # Step 4: Get answer from LLM
        response = self.llm.invoke(prompt)
        answer_text = response.content if hasattr(response, 'content') else str(response)
        
        # Step 5: Prepare source information (which pages helped answer)
        sources = []
        for i, doc in enumerate(docs):
            try:
                # Try to get page number from document metadata
                page_num = doc.metadata.get("page", i) if hasattr(doc, 'metadata') else i
                sources.append({
                    "page": int(page_num) if page_num else i,
                    "source": "Rainbow-Bazaar-Return-Refund-&-Cancellation-Policy.pdf"
                })
            except:
                # If anything fails, just use the index
                sources.append({
                    "page": i,
                    "source": "Rainbow-Bazaar-Return-Refund-&-Cancellation-Policy.pdf"
                })
        
        # Return question + answer + sources
        return {
            "question": question,
            "answer": answer_text,
            "sources": sources
        }


# Create global RAG instance - used by backend API
# This will be initialized when backend starts
rag = SimpleRAG()
