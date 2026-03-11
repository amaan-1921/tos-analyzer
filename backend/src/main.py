"""
Main entry point for the FastAPI application.

This module instantiates the FastAPI application, configures CORS middleware, manages uploads, and exposes
all required endpoints with different functionalities that are required for the application.
"""

import logging
import uuid
import os
import json
import shutil
import asyncio

from datetime import datetime
from ingest import ingest as ingested

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from langchain_setup import test_neo4j_connection
from models import ChatOut, QueryIn
from retrieve import generate_initial_analysis, get_similar_chunks, generate_rag_response

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set the upload directory for the various ToS uploads
UPLOAD_DIR = "./uploads"

# Global analysis state for progress tracking
analysis_state = {}

# Global tracking of current processing mode for chat
current_use_cloud_mode = False
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "8"))


def estimated_analysis_time(num_chunks: int) -> int:
    """
    Estimate analysis time in seconds based on chunk count.
    Rough calculation: ~3-4 seconds per chunk with parallel processing.
    """
    return max(30, int(num_chunks * 3.5))

# -----------------------------
# Lifespan handler
# -----------------------------
@asynccontextmanager
async def check_neo4j(app: FastAPI):
    """
    Startup event to check connection to Neo4j database.
    Calls the test_connection function from the langchain_setup script,
    and prints the status to the container logs.
    """
    try:
        test_neo4j_connection()
        logger.info("✅ Neo4j connection established.")
    except Exception as e:
        logger.error(f"❌ Neo4j connection failed: {e}")
    yield
    # (You could close the driver here if you have a global driver instance)


# -----------------------------
# Instantiate FastAPI application
# -----------------------------
app = FastAPI(title="ToS-Analyser", version="0.0.1", lifespan=check_neo4j)

# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)


# -----------------------------
# Routes
# -----------------------------
@app.get("/")
def get_root():
    """
    Root endpoint of the API.
    Returns a simple dictionary with a greeting and the current time.
    """
    return {
        "message": "Welcome to the ToS Analyzer API. Visit /docs for API documentation.",
        "time": datetime.now().isoformat(),
    }


@app.post("/ingest")
async def ingest(file: UploadFile = File(...), use_cloud: str = Form("false")):
    """
    Ingestion endpoint of the API.
    Uploads a document, assigns it a unique identifier, saves it, and starts analysis.
    
    Args:
        file: PDF/TXT file to analyze
        use_cloud: String "true" or "false" for cloud/local processing
    
    Returns immediately with doc_id and estimated time.
    """
    
    # Convert string to boolean
    use_cloud_bool = use_cloud.lower() == "true"
    logger.info(f"Received use_cloud={use_cloud} (type: {type(use_cloud)}), converted to bool: {use_cloud_bool}")

    doc_id = str(uuid.uuid4())
    try:
        ext = os.path.splitext(file.filename)[1]  # type: ignore
        dest = os.path.join(UPLOAD_DIR, f"{doc_id}{ext}")
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        with open(dest, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"File {file.filename} saved as {dest}")
        
        # Initialize analysis state
        analysis_state[doc_id] = {
            "status": "processing",
            "progress": 0,
            "message": "Chunking text and generating embeddings...",
            "result": None,
            "use_cloud": use_cloud_bool
        }
        
        # Run analysis asynchronously
        asyncio.create_task(run_analysis(doc_id, dest, use_cloud_bool))
        
        # Read first line to estimate chunk count (rough estimate)
        with open(dest, 'r', encoding='utf-8', errors='ignore') as f:
            text_sample = f.read(5000)  # Read first 5KB
            estimated_chunks = max(5, len(text_sample) // 1000)
            
            # Adjust estimate based on processing mode
            if use_cloud_bool:
                estimated_time = max(15, int(estimated_chunks * 1.5))  # Cloud is faster
            else:
                estimated_time = estimated_analysis_time(estimated_chunks)  # Local
        
        return {
            "doc_id": doc_id,
            "status": "started",
            "file_name": file.filename,
            "estimated_time": estimated_time,
            "processing_mode": "cloud (fast)" if use_cloud_bool else "local (private)",
            "message": f"Analysis will take approximately {estimated_time} seconds"
        }

    except Exception as e:
        logger.error(f"Failed to ingest file: {e}")
        if doc_id in analysis_state:
            del analysis_state[doc_id]
        raise HTTPException(status_code=422, detail=str(e))


async def run_analysis(doc_id: str, filepath: str, use_cloud: bool = False):
    """
    Run the actual analysis in the background.
    
    Args:
        doc_id: Document ID
        filepath: Path to uploaded file
        use_cloud: Whether to use cloud API for faster processing
    """
    try:
        analysis_state[doc_id]["message"] = "Extracting triples and analyzing..."
        analysis_state[doc_id]["progress"] = 25
        logger.info(f"Starting analysis for {doc_id} (cloud={use_cloud})")
        
        # Set global cloud mode for chat to use
        global current_use_cloud_mode
        current_use_cloud_mode = use_cloud
        logger.info(f"Set cloud mode to {use_cloud} for chat queries")
        
        # Run ingestion with progress tracking (blocking call, but in async context)
        json_analysis = await asyncio.to_thread(ingested, filepath, use_cloud, doc_id, analysis_state)
        logger.info(f"Ingestion returned: {len(json_analysis)} chars")
        
        # Parse the JSON
        parsed_result = json.loads(json_analysis)
        logger.info(f"Parsed result: {len(parsed_result)} clauses found")
        
        # Ensure result is a list
        if isinstance(parsed_result, dict):
            parsed_result = [parsed_result]
        
        analysis_state[doc_id]["progress"] = 100
        analysis_state[doc_id]["status"] = "completed"
        analysis_state[doc_id]["result"] = parsed_result
        analysis_state[doc_id]["message"] = "Analysis complete!"
        logger.info(f"Analysis completed for {doc_id} with {len(parsed_result)} findings")
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error for {doc_id}: {e}")
        analysis_state[doc_id]["status"] = "failed"
        analysis_state[doc_id]["message"] = f"JSON parsing error: {str(e)}"
    except Exception as e:
        logger.error(f"Analysis failed for {doc_id}: {e}", exc_info=True)
        analysis_state[doc_id]["status"] = "failed"
        analysis_state[doc_id]["message"] = f"Error: {str(e)}"


@app.get("/analysis/{doc_id}")
async def get_analysis(doc_id: str):
    """
    Get analysis progress and results for a document.
    Returns immediate status or full results when complete.
    """
    if doc_id not in analysis_state:
        raise HTTPException(status_code=404, detail="Document not found")
    
    state = analysis_state[doc_id]
    return {
        "doc_id": doc_id,
        "status": state["status"],
        "progress": state["progress"],
        "message": state["message"],
        "result": state["result"]
    }


@app.post("/query")
def query(q: QueryIn):
    """
    Querying endpoint of the RAG API.
    This endpoint queries the LLM, which uses RAG to give accurate answers.
    Uses Groq cloud API if analysis used cloud mode, otherwise uses local LLM.
    """
    try:
        retrieved_chunks = get_similar_chunks(q.query, k=RAG_TOP_K)
        if not retrieved_chunks:
            return ChatOut(chunks=[], response="No relevant sections were found.", retrieved_count=0, top_k=RAG_TOP_K)

        # Get analysis results if doc_id is provided
        analysis_results = None
        if q.doc_id and q.doc_id in analysis_state:
            analysis_results = analysis_state[q.doc_id].get("result")

        # Use cloud LLM for chat if analysis used cloud mode
        if current_use_cloud_mode:
            from langchain_setup import get_llm_models
            _, chat_llm = get_llm_models(use_cloud=True, for_chat=True)
            logger.info("Chat: Using Groq API (cloud mode)")
        else:
            from langchain_setup import llm as chat_llm
            logger.info("Chat: Using local Ollama (private mode)")
        
        response = generate_rag_response(q.query, retrieved_chunks, analysis_results=analysis_results, llm_model=chat_llm)

        return ChatOut(
            chunks=retrieved_chunks,
            response=response,
            retrieved_count=len(retrieved_chunks),
            top_k=RAG_TOP_K,
        )

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse analysis JSON from LLM: {e}")
        raise HTTPException(status_code=500, detail="Invalid JSON format from analysis")
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
