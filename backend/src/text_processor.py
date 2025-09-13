""""
Text Processing Utility.

This module provides basic text processing required for various RAG purposes 
like embedding generation, and chunking.
"""

from oopsies import PDFExtractionError, HTMLExtractionError, IngestionError

import os
import spacy
import re
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
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

def load_text(path: str) -> str:
    """
    Abstraction function to recognise the uploaded file's format
    and call the appropiate function to read the text and return
    the read string of text.

    Args:
        path (str): The filepath of the file to be read.

    Raises:
        FileNotFoundError: When the referenced file is not found /
        does not exist.

        GeneralIngestionError: When the referenced file is a PDF that cannot be read,
        or some other unexpected file error.

    Returns:
        str: The extracted text from the file referenced by the path
        parameter.
    """
    path = os.path.expanduser(path)
    _, ext = os.path.splitext(path)
    ext = ext.lower().lstrip(".")
    if ext == "pdf":
        return extract_pdf_text(path)
    elif ext == "txt":
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    elif ext == "html":
        return extract_html_text(path)
    else:
        raise IngestionError("Unsupported file type. Only use pdf, html, and txt") 


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
        raise PDFExtractionError(str(e)) from e

    return text

def extract_html_text(path: str) -> str:
    """
    Extracts the text in the HTML referenced bby th provided path

    Args:
        path (str): The filepath of the HTML document whose text is to extracted.

    Returns:
        str: The extracted text from the HTML file whose filepath is provided in a 
        single string.
    """
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    return text
