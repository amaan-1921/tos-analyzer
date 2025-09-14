"""
Model definitions

This file defines the various input and output models that
are used by the API.
"""

from typing import List, Dict, Optional

from pydantic import BaseModel

class QueryIn(BaseModel):
    query: str
    namespace: str # which document/KG to query

class QueryOut(BaseModel):
    query: str
    response: str
    context_chunks: Optional[List[Dict]]
