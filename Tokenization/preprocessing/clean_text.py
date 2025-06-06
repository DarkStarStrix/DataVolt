import re
import unicodedata

def clean_text(text: str) -> str:
    """Clean and normalize text for LLM ingestion."""
    if not isinstance(text, str):
        return ""
    # Normalize unicode
    text = unicodedata.normalize("NFKC", text)
    # Remove control characters
    text = re.sub(r"[\x00-\x1F\x7F]", " ", text)
    # Replace multiple spaces/newlines with a single space
    text = re.sub(r"\s+", " ", text)
    # Strip leading/trailing whitespace
    text = text.strip()
    return text
