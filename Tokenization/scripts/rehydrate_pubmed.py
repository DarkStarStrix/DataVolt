import time
from pathlib import Path
from typing import Optional

import pandas as pd
from Bio import Entrez

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
SOURCE_PATH = DATA_DIR / "Scientific_Research_Tokenized.parquet"
OUTPUT_PATH = DATA_DIR / "Scientific_Research_Tokenized_refilled.parquet"


def fetch_abstract(pmid: str) -> str:
    """Fetch abstract text for a given PubMed ID."""
    try:
        handle = Entrez.efetch(db="pubmed", id=pmid, rettype="abstract", retmode="text")
        text = handle.read().strip()
        handle.close()
        time.sleep(0.34)
        return text
    except Exception:
        return ""


def refill(row: pd.Series) -> pd.Series:
    """In-place enrichment of a dataset row with abstract/full text fallback."""
    prov = row.get("provenance", {})
    pmid = prov.get("pubmed_id") if isinstance(prov, dict) else None
    if not row.get("abstract") and pmid:
        row["abstract"] = fetch_abstract(str(pmid))
    if not row.get("full_text"):
        row["full_text"] = row["abstract"]
    row["text"] = row.get("full_text") or row.get("abstract") or row.get("title", "")
    return row


def rehydrate_pubmed_dataset(
    source_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
    email: Optional[str] = None,
) -> Path:
    """
    Rehydrate missing PubMed abstracts/full text and persist to Parquet.

    Args:
        source_path: Input dataset path. Defaults to `Scientific_Research_Tokenized.parquet`.
        output_path: Output dataset path. Defaults to `<input>_refilled.parquet`.
        email: Optional Entrez email override.

    Returns:
        Path to the refilled Parquet file.
    """
    if email:
        Entrez.email = email
    elif not Entrez.email:
        Entrez.email = "you@example.com"

    source = Path(source_path or SOURCE_PATH)
    if not source.exists():
        raise FileNotFoundError(f"Source dataset not found: {source}")

    target = Path(output_path or OUTPUT_PATH)
    df = pd.read_parquet(source)
    rehydrated = df.apply(refill, axis=1)
    target.parent.mkdir(parents=True, exist_ok=True)
    rehydrated.to_parquet(target)
    print(f"✅ Saved rehydrated dataset to {target}")
    return target


if __name__ == "__main__":
    rehydrate_pubmed_dataset()
