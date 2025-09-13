class PDFExtractionError(Exception):
    """Raised when a PDF cannot be processed or text cannot be extracted."""
    pass

class HTMLExtractionError(Exception):
    """Raised when an HTML file cannot be processed."""
    pass

class IngestionError(Exception):
    """General ingestion pipeline failure."""
    pass

