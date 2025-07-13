import spacy
import re
from typing import List

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def segment_clauses(text: str) -> List[str]:
    """Segment ToS text into clauses using spaCy and numbering patterns."""
    doc = nlp(text)
    clauses = []

    for sent in doc.sents:
        cleaned = sent.text.strip()

        # Split on numbered or lettered section patterns
        split_parts = re.split(r'(?<=\.)\s*(?=\d+\.)|(?<=\))\s*(?=\w)', cleaned)
        for part in split_parts:
            part = part.strip()
            if part:
                clauses.append(part)

    return clauses
