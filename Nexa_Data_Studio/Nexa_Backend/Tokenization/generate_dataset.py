import json
from typing import Optional, Callable, Dict, Any

from Nexa_Backend.Tokenization.Build_tokenizer import QLoRAPreprocessor
from Nexa_Backend.Tokenization.preprocessing.Clean_text import clean_text
from Nexa_Backend.Tokenization.Main_2 import ScientificCorpusBuilder, CorpusConfig

def generate_dataset(
    domain: str = None,
    token_budget: int = 1000,
    plan: str = "free",
    custom_seed: Optional[str] = None,
    job_type: str = "tokenize",
    progress_callback: Optional[Callable[[int, str], None]] = None
) -> Dict[str, Any]:
    """
    Unified dataset generation pipeline for both 'tokenize' and 'corpus' jobs.

    Args:
        domain (str): Domain for dataset.
        token_budget (int): Token budget.
        plan (str): Plan type.
        custom_seed (str): Optional seed data.
        job_type (str): "tokenize" or "corpus".
        progress_callback (callable): Progress update callback.

    Returns:
        dict: {"jsonl_lines": [...], "stats": {...}}
    """
    if job_type == "corpus":
        # Use Main_2 pipeline
        if progress_callback:
            progress_callback(1, "Initializing scientific corpus builder...")
        config = CorpusConfig()
        builder = ScientificCorpusBuilder(config)
        if progress_callback:
            progress_callback(2, "Fetching arXiv papers...")
        arxiv_papers = builder.fetch_arxiv_papers()
        if progress_callback:
            progress_callback(3, "Fetching PubMed papers...")
        pubmed_papers = builder.fetch_pubmed_papers()
        if progress_callback:
            progress_callback(4, "Fetching FineWeb-Edu samples...")
        fineweb_papers = builder.fetch_fineweb_edu()
        if progress_callback:
            progress_callback(5, "Processing and tagging papers...")
        all_papers = []
        all_papers.extend(builder.process_papers(arxiv_papers, "arxiv"))
        all_papers.extend(builder.process_papers(pubmed_papers, "biology"))
        all_papers.extend(builder.process_papers(fineweb_papers, "education"))
        if progress_callback:
            progress_callback(6, "Ranking and deduplicating...")
        ranked_papers = builder.ranker.rank_samples(all_papers)
        if progress_callback:
            progress_callback(7, "Preparing dataset for download...")
        jsonl_lines = [json.dumps(paper, ensure_ascii=False) for paper in ranked_papers]
        stats = builder.analyzer.get_dataset_stats(ranked_papers)
        if progress_callback:
            progress_callback(8, "Dataset ready for download.")
        return {"jsonl_lines": jsonl_lines, "stats": stats}

    # Standard "tokenize" job
    if progress_callback:
        progress_callback(1, "Cleaning input text...")
    cleaned_text = clean_text(custom_seed or "")
    if progress_callback:
        progress_callback(2, "Tokenizing input...")
    preprocessor = QLoRAPreprocessor()
    # For demonstration, just split cleaned_text into sentences (replace with real logic)
    tokens = [cleaned_text[i:i+token_budget] for i in range(0, len(cleaned_text), token_budget)]
    if progress_callback:
        progress_callback(3, "Formatting samples...")
    jsonl_lines = [json.dumps({"text": t}) for t in tokens]
    stats = {"token_count": sum(len(t.split()) for t in tokens), "total_samples": len(tokens)}
    if progress_callback:
        progress_callback(4, "Dataset ready for download.")
    return {"jsonl_lines": jsonl_lines, "stats": stats}
