"""
Text Processing Utility.

This module provides basic text processing required for various RAG purposes 
like embedding generation, and chunking.
"""

import spacy
import re
from PyPDF2 import PdfReader
from typing import List

# Load spaCy model
nlp = spacy.load("en_core_web_sm")


def segment_clauses(text: str) -> List[str]:
    """
    Generates a list of clauses from a string of collection of clauses.

    Args:
        text (str): The string which is to be segmented into clauses. 

    Returns:
        List[str]: A list of strings, where each string is a self contained
                   clause in English language.
    """
    doc = nlp(text)
    clauses = []

    for sent in doc.sents:
        cleaned = sent.text.strip()
        split_parts = re.split(
            r'(?<=\.)\s*(?=\d+\.)|(?<=\))\s*(?=\w)', cleaned)
        for part in split_parts:
            part = part.strip()
            if part:
                clauses.append(part)

    return clauses

def extract_pdf_text(path: str) -> str:
    """
    Extracts the text in the PDF referenced by the provided path.

    Args:
        path (str): The filepath of the PDF whose text is to be extracted.

    Raises:
        Exception: When the PDF cannot be read.

    Returns:
        str: The extracted text from the PDF whose filepath is provided in
        a single string.
    """
    try:
        reader = PdfReader(path)
        text = ""
        n = len(reader.pages)
        for i in range(n):
            text = text + "\n" + reader.pages[i].extract_text()

    except Exception as e:
        raise Exception(str(e))

    return text
