from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import logging
from .model_predictor import ToSModel
from .text_processor import segment_clauses

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware first
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)

tos_model = ToSModel()

class AnalyzeRequest(BaseModel):
    text: str

class ResultItem(BaseModel):
    clause_number: int
    text: str
    label: str
    explanation: str

class AnalyzeResponse(BaseModel):
    results: List[ResultItem]

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_tos(request: AnalyzeRequest):
    try:
        text = request.text.rstrip('.')
        clauses = segment_clauses(text)
        if not clauses:
            logger.info("No valid clauses found in input text")
            return {"results": []}

        logger.debug(f"Input text: {request.text}")
        logger.debug(f"Split clauses: {clauses}")
        results = tos_model.predict(clauses)
        return {"results": results}
    except Exception as e:
        logger.error(f"Endpoint error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Welcome to the ToS Analyzer API. Visit /docs for API documentation."}