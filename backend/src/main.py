"""
Main entry point for the FastAPI application.

This module instantiates the FastAPI application, confiures CORS middleware, manages uploads, and exposes 
all required endpoints with different functionalities that are required for the application.
"""

from contextlib import asynccontextmanager
import logging
import uuid
import os
import shutil
from datetime import datetime

from fastapi import FastAPI, HTTPException, UploadFile, File, status
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from langchain_setup import test_connection

from models import QueryIn

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Instiate the FastAPI application
# `title` and `version` are used for OpenAPI docs.
app = FastAPI(title="ToS-Analyser", version="0.0.1")

# Define allowed origins for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)

# Set the upload directory for the various ToS uploads
UPLOAD_DIR = "./uploads"

@asynccontextmanager
async def check_neo4j():
    """
    Startup event to check connection to Neo4j database.
    Calls the test_connection function from the langchain_setup script,
    and prints the status to the container logs
    """
    try:
        test_connection()
        print("Connection made.")
    except Exception as e:
        print("Connection not made.")
    yield


@app.get("/")
def get_root():
    """
    Root endpoint of the API.

    This endpoints returns a basic health check and a welcome message.
    It returns a simple dictionary with a greeting and the current time.

    Returns:
        dict: A dictionary containing a greeting and the current timestamp.
    """
    return {
            "message": "Welcome to the ToS Analyzer API. Visit /docs for API documentation.", 
            "time": datetime.now().isoformat()
            }


@app.post("/ingest")
def ingest(file: UploadFile = File(...)):
    """
    Ingestion endpoint of the API.

    This endpoint uploads a document assigns it a unique identifier and
    copies the file onto the server upload folder. This file is then ingested
    using the ingestion pipeline.

    Args:
        file (UploadFile): Required uploaded ToS file.

    Raises:
        RequestValidationError:
            - 422 Unprocessable Entity: When the file is not provided or does not have an extenstion.

    Returns:
        Dict: A dictionary containing the document identifier and the ingestion response
    """
    doc_id = str(uuid.uuid4())
    try:
        ext = os.path.splitext(file.filename)[1]
        dest = os.path.join(UPLOAD_DIR, f"{doc_id}{ext}")
        with open(dest, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        # call ingestion util

    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    return {"doc_id": doc_id, "status": "ingested"}

@app.post("/query")
def query(q: QueryIn):
    """
    Querying endpoint of the RAG API.

    This endpoint queries the LLM, which uses RAG to give accurate answers.
    The function simply calls the retrieval function answer_query defined in
    retrieval.py.

    Args:
        q (models.QueryIn): The input query, which is a QueryIn class; contains
        the query text and the namespace (doc_id).

    Raises:
        HTTPException:
            - 500 Internal Server Error: When something goes wrong with the retrival.

    Returns:
        dict: A dictionary containing a structured response generated through the RAG.
    """
    response = {} # placeholder
    try:
        # get response by call retreiver util
        pass
    
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))

    return response
