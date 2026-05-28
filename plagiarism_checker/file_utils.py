"""
plagiarism_checker/file_utils.py

Utilities for extracting raw text from uploaded files.
Supports .txt and .pdf formats.
"""

import logging

logger = logging.getLogger(__name__)


def extract_text_from_file(uploaded_file) -> tuple[str, str]:
    """
    Extract text content from an uploaded Django InMemoryUploadedFile or TemporaryUploadedFile.

    Returns:
        (text: str, file_type: str)   where file_type is 'txt' or 'pdf'

    Raises:
        ValueError: if the file type is not supported or extraction fails.
    """
    filename = uploaded_file.name.lower()

    if filename.endswith(".txt"):
        return _extract_txt(uploaded_file), "txt"
    elif filename.endswith(".pdf"):
        return _extract_pdf(uploaded_file), "pdf"
    else:
        raise ValueError(
            f"Unsupported file type: '{uploaded_file.name}'. "
            "Please upload a .txt or .pdf file."
        )


def _extract_txt(uploaded_file) -> str:
    """Read and decode a plain-text file. Tries UTF-8 first, then latin-1."""
    try:
        content = uploaded_file.read()
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return content.decode("latin-1")
    except Exception as e:
        raise ValueError(f"Could not read text file: {e}") from e


def _extract_pdf(uploaded_file) -> str:
    """
    Extract text from a PDF using PyPDF2.
    Iterates all pages and joins their text with newlines.
    """
    try:
        import PyPDF2
    except ImportError:
        raise ImportError("PyPDF2 is not installed. Run: pip install PyPDF2")

    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        pages_text = []
        for page_num, page in enumerate(reader.pages):
            try:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
            except Exception as e:
                logger.warning("Could not extract text from page %d: %s", page_num, e)

        full_text = "\n".join(pages_text).strip()

        if not full_text:
            raise ValueError(
                "No text could be extracted from this PDF. "
                "It may be a scanned image or a protected file."
            )

        return full_text

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Could not read PDF file: {e}") from e


def validate_file(uploaded_file) -> None:
    """
    Validate that the file meets our requirements before processing.
    Raises ValueError with a user-friendly message on failure.
    """
    MAX_SIZE_MB = 10
    MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024

    if uploaded_file.size > MAX_SIZE_BYTES:
        raise ValueError(
            f"File is too large ({uploaded_file.size / 1024 / 1024:.1f} MB). "
            f"Maximum allowed size is {MAX_SIZE_MB} MB."
        )

    filename = uploaded_file.name.lower()
    if not (filename.endswith(".txt") or filename.endswith(".pdf")):
        raise ValueError(
            f"Unsupported file type: '{uploaded_file.name}'. "
            "Only .txt and .pdf files are accepted."
        )