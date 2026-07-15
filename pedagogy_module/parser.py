import fitz  # PyMuPDF
import pypdf
import os
import io
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_content: bytes) -> str:
    """
    Extracts raw text from PDF content (bytes) using PyMuPDF (fitz) as the primary parser,
    and pypdf as a fallback.
    """
    text = ""
    try:
        # Try PyMuPDF first
        doc = fitz.open(stream=pdf_content, filetype="pdf")
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()
        logger.info("Successfully extracted text from PDF using PyMuPDF.")
    except Exception as e:
        logger.warning(f"PyMuPDF extraction failed: {e}. Falling back to pypdf.")
        try:
            # Fallback to pypdf
            pdf_file = io.BytesIO(pdf_content)
            reader = pypdf.PdfReader(pdf_file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            logger.info("Successfully extracted text from PDF using pypdf fallback.")
        except Exception as fallback_err:
            logger.error(f"Fallback pypdf extraction also failed: {fallback_err}")
            raise ValueError(f"Failed to parse PDF document: {fallback_err}")

    # Basic cleaning: remove empty lines and strip whitespace
    cleaned_lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            cleaned_lines.append(stripped)
            
    return "\n".join(cleaned_lines)
