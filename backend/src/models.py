"""
Model definitions

This file defines the various input and output models that
are used by the API.
"""

from typing import List, Dict, Optional

from pydantic import BaseModel

class QueryIn(BaseModel):
    query: str

class QueryOut(BaseModel):
    clause_text: str
    label: str
    reasoning: str
    risk_category: str

class ChatOut(BaseModel):
    chunks: List[Dict]
    response: str
