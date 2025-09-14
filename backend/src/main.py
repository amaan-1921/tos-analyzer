"""
Main entry point for the FastAPI application.

This module instantiates the FastAPI application, configures CORS middleware, manages uploads, and exposes
all required endpoints with different functionalities that are required for the application.
"""

from contextlib import asynccontextmanager
import logging
import uuid
import os
import shutil
from datetime import datetime
from ingest import ingest as ingested
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from langchain_setup import test_neo4j_connection
from models import QueryIn

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set the upload directory for the various ToS uploads
UPLOAD_DIR = "./uploads"

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
def ingest(file: UploadFile = File(...)):
    """
    Ingestion endpoint of the API.
    Uploads a document, assigns it a unique identifier, and saves it.
    """

    doc_id = str(uuid.uuid4())
    try:
        ext = os.path.splitext(file.filename)[1]  # type: ignore
        dest = os.path.join(UPLOAD_DIR, f"{doc_id}{ext}")
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        with open(dest, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        # TODO: call ingestion util here
        logger.info(f"File {file.filename} saved as {dest}")
        ingested(dest)

    except Exception as e:
        logger.error(f"Failed to ingest file: {e}")
        raise HTTPException(status_code=422, detail=str(e))

    return {"doc_id": doc_id, "status": "ingested"}


@app.post("/query")
def query(q: QueryIn):
    """
    Querying endpoint of the RAG API.
    This endpoint queries the LLM, which uses RAG to give accurate answers.
    """
    try:
        # TODO: call retriever util here
        response = {"answer": "This is a placeholder."}
        return response
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
