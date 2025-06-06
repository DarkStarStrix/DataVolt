import re

def segment_paragraphs(text: str) -> list:
    """Segment text into paragraphs using double newlines or similar heuristics."""
    if not isinstance(text, str):
        return []
    # Split on two or more newlines, or at least 200 chars per paragraph
    paras = re.split(r"\n{2,}", text)
    # Fallback: split-long paragraphs
    result = []
    for para in paras:
        para = para.strip()
        if len(para) > 1000:
            # Split further if too long
            chunks = [para[i:i+1000] for i in range(0, len(para), 1000)]
            result.extend(chunks)
        elif para:
            result.append(para)
    return [p for p in result if p]
