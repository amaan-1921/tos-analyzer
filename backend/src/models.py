"""
Model definitions

This file defines the various input and output models that
are used by the API.
"""

from pydantic import BaseModel

class QueryIn(BaseModel):
    query: str
    namespace: str # which document/KG to query
