from typing import Dict, List
from Tokenization.preprocessing.clean_text import clean_text
from Tokenization.preprocessing.segment_paragraphs import segment_paragraphs

def preprocess_sample(paper: Dict) -> List[Dict]:
    """
    Clean and segment a paper into samples for LLM ingestion.
    Returns a list of dicts: one for title+abstract, and one per paragraph.
    """
    title = clean_text(paper.get("title", ""))
    abstract = clean_text(paper.get("abstract", ""))
    full_text = clean_text(paper.get("full_text", ""))
    paragraphs = segment_paragraphs(full_text) if full_text else []
    samples = []
    # Title + abstract sample
    if title or abstract:
        sample = dict(paper)
        sample["title"] = title
        sample["abstract"] = abstract
        sample["full_text"] = ""
        sample["section"] = "abstract"
        samples.append(sample)
    # Paragraph samples
    for para in paragraphs:
        sample = dict(paper)
        sample["title"] = title
        sample["abstract"] = ""
        sample["full_text"] = para
        sample["section"] = "paragraph"
        samples.append(sample)
    return samples
