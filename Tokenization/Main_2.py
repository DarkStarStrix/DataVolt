# python
"""
The Main pipeline for building a scientific corpus from multiple sources.

Responsibilities:
- Orchestrates collection, processing, ranking, and deduplication of papers from arXiv, PubMed, and FineWeb-Edu.
- Handles error logging, checkpointing, and metrics for observability.
- Modular design for extensibility and maintainability.

Usage:
    python Main_2.py

Classes:
    - SourceMetrics: Tracks per-source metrics.
    - CorpusConfig: Configuration for corpus building.
    - ScientificCorpusBuilder: Main pipeline class.

Functions:
    - main: Entry point for running the pipeline.

Environment:
    - Requires ENTREZ_EMAIL for PubMed API.
    - Outputs logs and intermediate checkpoints to ./scientific_corpus_data.

"""

import concurrent.futures
import json
import logging
import os
import signal
import time
from dataclasses import dataclass
from pathlib import Path
from types import FrameType
from typing import List, Dict, Set, Optional, Callable, Any
from urllib.error import URLError, HTTPError
from xml.parsers.expat import ExpatError

import arxiv
from Bio import Entrez
from datasets import load_dataset
from tqdm import tqdm

from Tokenization.Build_tokenizer import QLoRAPreprocessor
from Tokenization.entropy_ranker import EntropyRanker
from Tokenization.hf_upload import upload_to_huggingface
from Tokenization.label_tokens import TASK_TAGS, ROUTING_TAGS
from Tokenization.preprocessing import clean_text, segment_paragraphs
from Tokenization.pretraining.dataset_stats import DatasetAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("corpus_builder.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


is_shutdown = False
"""Global flag indicating whether a shutdown signal has been received.

This flag is set to True by the signal handler to allow for graceful shutdown
of long-running operations throughout the pipeline.
"""

def signal_handler(sig: int, frame: FrameType) -> None:
    """Handle shutdown signals gracefully and set shutdown flag."""
    global is_shutdown
    logger.info(f"Received signal {sig}, shutting down gracefully. Frame: {frame}")
    is_shutdown = True


# Register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def retry(max_retries: int = 3, backoff_factor: float = 1.0,
          exceptions: tuple = (Exception,)) -> Callable:
    """
    Decorator for retrying a function with exponential backoff.

    Args:
        max_retries: Maximum number of retries.
        backoff_factor: Multiplier for exponential backoff.
        exceptions: Exception types to catch and retry.

    Returns:
        Decorated function with retry logic.
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            retries = 0
            while retries < max_retries:
                if is_shutdown:
                    logger.info("Shutdown in progress, aborting retries.")
                    raise KeyboardInterrupt("Shutdown requested")
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    wait = backoff_factor * (2 ** retries)
                    logger.warning(f"Error in {func.__name__}: {e}. Retrying in {wait:.1f}s...")
                    time.sleep(wait)
                    retries += 1
            logger.error(f"Function {func.__name__} failed after {max_retries} attempts.")
            raise RuntimeError(f"{func.__name__} failed after {max_retries} attempts")
        return wrapper
    return decorator


@dataclass
class SourceMetrics:
    """Metrics for tracking source performance."""
    papers: int = 0
    tokens: int = 0
    time: float = 0.0
    errors: int = 0


@dataclass
class CorpusConfig:
    """
    Configuration for corpus building parameters.

    Attributes:
        max_arxiv_papers: Maximum number of arXiv papers to fetch.
        max_pubmed_papers: Maximum number of PubMed papers to fetch.
        max_fineweb_samples: Maximum number of FineWeb-Edu samples to fetch.
        max_workers: Number of workers for parallel processing.
        timeout: Timeout for API requests.
        chunk_size: Chunk size for batch processing.
    """
    max_arxiv_papers: int = 9000
    max_pubmed_papers: int = 3000
    max_fineweb_samples: int = 30000
    max_workers: int = 8
    timeout: int = 30
    chunk_size: int = 1000


class ScientificCorpusBuilder:
    """
    Main class for building a scientific corpus from multiple sources.

    Methods:
        fetch_arxiv_papers: Collects papers from arXiv.
        fetch_pubmed_papers: Collects papers from PubMed.
        fetch_fineweb_edu: Collects educational content from FineWeb-Edu.
        preprocess_sample: Cleans and segments a paper into samples.
        process_papers: Tags, filters, and preprocesses papers.
        build_corpus: Orchestrates the full pipeline and builds the corpus.
        print_report: Prints a summary report of the build process.
    """

    def __init__(self, config: Optional[CorpusConfig] = None):
        """
        Initialize the corpus builder with configuration and dependencies.

        Args:
            config: Optional CorpusConfig object.
        """
        self.config = config or CorpusConfig()
        self.preprocessor = QLoRAPreprocessor(corpus_type="scientific")
        self.analyzer = DatasetAnalyzer()
        self.ranker = EntropyRanker()
        self.data_dir = Path("scientific_corpus_data")
        self.data_dir.mkdir(exist_ok=True)
        self._setup_apis()
        self.seen_titles: Set[str] = set()
        self.metrics = {
            "arxiv": SourceMetrics(),
            "pubmed": SourceMetrics(),
            "fineweb_edu": SourceMetrics(),
            "total_tokens": 0,
            "total_time": 0.0
        }

    @staticmethod
    def _setup_apis() -> None:
        """
        Setup API configurations for external data sources.
        """
        Entrez.email = os.getenv("ENTREZ_EMAIL", "your.email@example.com")
        if Entrez.email == "your.email@example.com":
            logger.warning("Using default email for Entrez. Set ENTREZ_EMAIL environment variable.")

    @retry(max_retries=3, backoff_factor=2,
           exceptions=(arxiv.ArxivError, HTTPError, URLError, ConnectionError))
    def _fetch_arxiv_search(self, query: str, max_results: int) -> List[Any]:
        """
        Fetch arXiv search results with error handling and exponential backoff.

        Args:
            query: arXiv API query string.
            max_results: Maximum number of results to fetch.

        Returns:
            List of arXiv result objects.
        """
        try:
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
            )
            client = arxiv.Client()
            results = list(client.results(search))
            if not results:
                logger.warning(f"Empty page returned for query '{query}'")
            return results
        except (arxiv.UnexpectedEmptyPageError, arxiv.HTTPError) as e:
            logger.warning(f"Empty page returned for query '{query}': {e}")
            return []
        except Exception as e:
            logger.error(f"Error in _fetch_arxiv_search for query '{query}': {e}")
            raise

    def fetch_arxiv_papers(self) -> List[Dict]:
        """
        Fetch papers from arXiv across multiple domains with verification and checkpoint saving.

        Returns:
            List of arXiv paper dictionaries.
        """
        logger.info("Starting arXiv paper collection...")
        start_time = time.time()
        papers = []
        queries = [
            ("physics", "cat:physics* OR cat:astro-ph* OR cat:cond-mat* OR cat:hep-th OR cat:quant-ph OR cat:math-ph"),
            ("biology", "cat:q-bio*"),
            ("materials", "cat:cond-mat.mtrl-sci OR cat:materials*")
        ]
        for domain, query in queries:
            if is_shutdown:
                break
            try:
                results = self._fetch_arxiv_search(query, self.config.max_arxiv_papers // 3)
                for result in tqdm(results, desc=f"arXiv {domain}"):
                    if is_shutdown:
                        break
                    try:
                        paper = {
                            "title": result.title.strip() if result.title else "",
                            "abstract": result.summary.strip() if result.summary else "",
                            "full_text": "",
                            "domain": domain,
                            "section": "abstract",
                            "source": "arxiv",
                            "authors": [str(a) for a in result.authors] if result.authors else [],
                            "published": result.published.isoformat() if result.published else None,
                            "provenance": {"arxiv_id": result.get_short_id()},
                            "categories": [c for c in getattr(result, "categories", [])] if hasattr(result, "categories") else [],
                            "text": result.summary.strip() if result.summary else ""
                        }
                        if paper["title"] and paper["title"] not in self.seen_titles:
                            papers.append(paper)
                            self.seen_titles.add(paper["title"])
                    except Exception as e:
                        logger.warning(f"Error processing arXiv result: {e}")
                        self.metrics["arxiv"].errors += 1
                        continue
            except Exception as e:
                logger.error(f"arXiv {domain} search failed: {e}")
                self.metrics["arxiv"].errors += 1
        self._save_intermediate(papers, "arxiv_papers.jsonl")
        elapsed = time.time() - start_time
        self.metrics["arxiv"].papers = len(papers)
        self.metrics["arxiv"].time = elapsed
        logger.info(f"Collected {len(papers)} arXiv papers in {elapsed:.2f}s")
        return papers

    @retry(max_retries=3, backoff_factor=2,
           exceptions=(HTTPError, URLError, ConnectionError, ExpatError))
    def _fetch_pubmed_batch(self, chunk_pmids: List[str]) -> Dict:
        """
        Fetch a batch of PubMed records with error handling.

        Args:
            chunk_pmids: List of PubMed IDs.

        Returns:
            Dictionary of PubMed records.
        """
        try:
            fetch_handle = Entrez.efetch (
                db="pubmed",
                id=",".join (chunk_pmids),
                rettype="medline",
                retmode="xml"
            )
            records = Entrez.read (fetch_handle)
            fetch_handle.close ()
            return records
        except ExpatError as e:
            logger.error (f"XML parsing error in PubMed batch: {e}")
            raise
        except (HTTPError, URLError) as e:
            logger.error (f"Network error fetching PubMed batch: {e}")
            raise

    def fetch_pubmed_papers(self) -> List[Dict]:
        """
        Fetch papers from PubMed with biology focus.

        Returns:
            List of PubMed paper dictionaries.
        """
        logger.info ("Starting PubMed paper collection...")
        start_time = time.time ()
        papers = []

        search_terms = [
            "(methods[Title/Abstract]) AND (biology[MeSH Terms])",
            "(computational biology[MeSH Terms]) AND (methods[Title/Abstract])",
            "(bioinformatics[MeSH Terms]) AND (algorithm[Title/Abstract])",
            "(molecular biology[MeSH Terms]) AND (technique[Title/Abstract])"
        ]

        for search_term in search_terms:
            if is_shutdown:
                break

            try:
                handle = Entrez.esearch (
                    db="pubmed",
                    term=search_term,
                    retmax=self.config.max_pubmed_papers // len (search_terms),
                    sort="relevance"
                )
                record = Entrez.read (handle)
                handle.close ()
                pmids = record.get ("IdList", [])

                for i in tqdm (range (0, len (pmids), self.config.chunk_size), desc="PubMed batch"):
                    if is_shutdown:
                        break

                    chunk_pmids = pmids [i:i + self.config.chunk_size]
                    try:
                        records = self._fetch_pubmed_batch (chunk_pmids)

                        for rec in records.get ("PubmedArticle", []):
                            try:
                                medline_citation = rec.get ("MedlineCitation", {})
                                article = medline_citation.get ("Article", {})

                                title = article.get ("ArticleTitle", "")
                                abstract_list = article.get ("Abstract", {}).get ("AbstractText", [""])
                                abstract = abstract_list [0] if abstract_list else ""

                                if title and isinstance (title, str) and title not in self.seen_titles:
                                    paper = {
                                        "title": title.strip (),
                                        "abstract": abstract.strip () if isinstance (abstract, str) else "",
                                        "full_text": "",
                                        "domain": "biology",
                                        "section": "abstract",
                                        "source": "pubmed",
                                        "authors": [],
                                        "published": None,
                                        "provenance": {"pubmed_id": str (medline_citation.get ("PMID", ""))},
                                        "categories": ["biology"],
                                        "text": abstract.strip () if isinstance (abstract, str) else ""
                                    }
                                    papers.append (paper)
                                    self.seen_titles.add (title)

                            except (KeyError, TypeError, AttributeError) as e:
                                logger.warning (f"Error processing PubMed record: {e}")
                                self.metrics ["pubmed"].errors += 1
                                continue

                    except (HTTPError, URLError, ConnectionError, ExpatError) as e:
                        self.metrics ["pubmed"].errors += 1
                        logger.warning (f"Failed to fetch PubMed batch: {e}")
                        continue

            except (HTTPError, URLError, ConnectionError, ExpatError) as e:
                self.metrics ["pubmed"].errors += 1
                logger.error (f"PubMed search failed for {search_term}: {e}")
            except KeyboardInterrupt:
                logger.info ("PubMed collection interrupted by user")
                break

        self._save_intermediate (papers, "pubmed_papers.jsonl")
        elapsed = time.time () - start_time
        self.metrics ["pubmed"].papers = len (papers)
        self.metrics ["pubmed"].time = elapsed
        logger.info (f"Collected {len (papers)} PubMed papers in {elapsed:.2f}s")
        return papers

    @retry (max_retries=3, backoff_factor=2,
            exceptions=(ConnectionError, HTTPError, URLError, OSError))
    def fetch_fineweb_edu(self) -> List [Dict]:
        """
        Fetch educational content from FineWeb-Edu dataset.

        Returns:
            List of FineWeb-Edu paper dictionaries.
        """
        logger.info ("Starting FineWeb-Edu collection...")
        start_time = time.time ()
        papers = []

        try:
            ds = load_dataset ("HuggingFaceFW/fineweb-edu", "sample-10BT",
                               split="train", streaming=True)
            samples = []

            for i, sample in enumerate (ds):
                if is_shutdown:
                    break
                if i >= self.config.max_fineweb_samples:
                    break

                if not isinstance (sample, dict) or "text" not in sample:
                    logger.warning (f"Invalid sample structure at index {i}")
                    continue

                samples.append (sample)
                if (i + 1) % 10000 == 0:
                    logger.info (f"Collected {i + 1} FineWeb samples")

            logger.info (f"Processing {len (samples)} FineWeb samples")

            def is_educational_content(sample: Dict) -> bool:
                """Check if content is educational and suitable."""
                try:
                    text = sample.get ("text", "")
                    if not isinstance (text, str) or len (text) < 500:
                        return False
                    return self.ranker.is_explanatory (text)
                except (AttributeError, TypeError, ValueError) as e:
                    logger.debug (f"Error evaluating educational content: {e}")
                    return False

            with concurrent.futures.ThreadPoolExecutor (max_workers=self.config.max_workers) as executor:
                filtered_results = list (tqdm (
                    executor.map (is_educational_content, samples),
                    total=len (samples),
                    desc="Filtering FineWeb content"
                ))

            for sample, is_good in zip (samples, filtered_results):
                if is_shutdown:
                    break
                if is_good:
                    try:
                        url = sample.get ("url", "")
                        meta = sample.get ("meta", {})
                        title = meta.get ("title", "") if isinstance (meta, dict) else ""
                        title = title or url or f"Document_{len (papers)}"

                        if title not in self.seen_titles:
                            paper = {
                                "title": title,
                                "abstract": "",
                                "full_text": sample.get ("text", ""),
                                "domain": "education",
                                "section": "full_text",
                                "source": "fineweb_edu",
                                "authors": [],
                                "published": None,
                                "provenance": {"url": url},
                                "categories": ["education"],
                                "text": sample.get("text", "")
                            }
                            papers.append (paper)
                            self.seen_titles.add (title)
                    except (KeyError, TypeError, AttributeError) as e:
                        logger.warning (f"Error processing FineWeb sample: {e}")
                        self.metrics ["fineweb_edu"].errors += 1
                        continue

        except (ConnectionError, HTTPError, URLError, OSError) as e:
            logger.error (f"FineWeb-Edu fetch failed: {e}")
            self.metrics ["fineweb_edu"].errors += 1
        except KeyboardInterrupt:
            logger.info ("FineWeb-Edu collection interrupted by user")
        except ImportError as e:
            logger.error (f"Failed to import required dataset library: {e}")
            self.metrics ["fineweb_edu"].errors += 1

        self._save_intermediate (papers, "fineweb_edu.jsonl")
        elapsed = time.time () - start_time
        self.metrics ["fineweb_edu"].papers = len (papers)
        self.metrics ["fineweb_edu"].time = elapsed
        logger.info (f"Collected {len (papers)} FineWeb-Edu papers in {elapsed:.2f}s")
        return papers

    @staticmethod
    def preprocess_sample(paper: Dict) -> List [Dict]:
        """
        Preprocess a paper sample into multiple training samples.

        Args:
            paper: Dictionary representing a paper.

        Returns:
            List of processed sample dictionaries.
        """
        try:
            title = clean_text (paper.get ("title", "")) if paper.get ("title") else ""
            abstract = clean_text (paper.get ("abstract", "")) if paper.get ("abstract") else ""
            full_text = clean_text (paper.get ("full_text", "")) if paper.get ("full_text") else ""

            paragraphs = segment_paragraphs (full_text) if full_text else []
            samples = []

            if title or abstract:
                sample = dict (paper)
                sample ["title"] = title
                sample ["abstract"] = abstract
                sample ["full_text"] = ""
                sample ["section"] = "abstract"
                samples.append (sample)

            for para in paragraphs:
                if para.strip ():
                    sample = dict (paper)
                    sample ["title"] = title
                    sample ["abstract"] = ""
                    sample ["full_text"] = para
                    sample ["section"] = "paragraph"
                    samples.append (sample)

            return samples

        except (AttributeError, TypeError, ValueError) as e:
            logger.warning (f"Error preprocessing sample: {e}")
            return []

    def process_papers(self, papers: List[Dict], domain: str) -> List[Dict]:
        """
        Process papers with domain-specific tagging and filtering.

        Args:
            papers: List of paper dictionaries.
            domain: Domain string for tagging.

        Returns:
            List of processed and filtered sample dictionaries.
        """
        logger.info(f"Processing {len(papers)} {domain} papers...")
        processed = []
        unknown_domains = 0
        unknown_sections = 0

        def label_domain(paper):
            cats = paper.get('categories', [])
            if not cats:
                return 'unknown'
            cats_str = " ".join(cats).lower()
            if 'bio' in cats_str:
                return '[BIO]'
            if 'gen' in cats_str:
                return '[GEN]'
            if 'phys' in cats_str:
                return '[PHY]'
            if 'math' in cats_str:
                return '[MATH]'
            if 'mat' in cats_str or 'materials' in cats_str:
                return '[MAT]'
            if 'astro' in cats_str:
                return '[ASTRO]'
            if 'cs' in cats_str:
                return '[CS]'
            return 'unknown'

        def label_section(paper):
            text = paper.get('text', '') or paper.get('abstract', '') or ''
            text_lower = text.lower()
            if not text_lower:
                return 'unknown'
            if 'abstract' in text_lower:
                return '[ABSTRACT]'
            if 'introduction' in text_lower:
                return '[INTRO]'
            if 'methods' in text_lower:
                return '[METHODS]'
            if 'results' in text_lower:
                return '[RESULTS]'
            if 'discussion' in text_lower:
                return '[DISCUSSION]'
            if 'conclusion' in text_lower:
                return '[CONCLUSION]'
            return 'unknown'

        for paper in tqdm(papers, desc=f"Processing {domain} papers"):
            try:
                domain_tag = label_domain(paper)
                section_tag = label_section(paper)
                paper["domain_tag"] = domain_tag
                paper["section_tag"] = section_tag
                if domain_tag == 'unknown':
                    unknown_domains += 1
                if section_tag == 'unknown':
                    unknown_sections += 1

                task = paper.get("task", None)
                if task and task in TASK_TAGS:
                    paper["task_tag"] = TASK_TAGS[task]

                routing = paper.get("routing", "general")
                paper["routing_tag"] = ROUTING_TAGS.get(routing, ROUTING_TAGS["general"])

                samples = self.preprocess_sample(paper)

                for sample in samples:
                    try:
                        content_parts = []
                        if sample.get("title"):
                            content_parts.append(str(sample["title"]))
                        if sample.get("abstract"):
                            content_parts.append(str(sample["abstract"]))
                        if sample.get("full_text"):
                            content_parts.append(str(sample["full_text"])[:1000])
                        content = " ".join(content_parts)
                        if content.strip() and self.ranker.is_explanatory(content):
                            sample["domain_tag"] = paper["domain_tag"]
                            sample["section_tag"] = paper["section_tag"]
                            sample["routing_tag"] = paper["routing_tag"]
                            if "task_tag" in paper:
                                sample["task_tag"] = paper["task_tag"]
                            processed.append(sample)
                    except Exception as e:
                        logger.debug(f"Error evaluating sample content: {e}")
                        continue

            except Exception as e:
                logger.warning(f"Paper processing error: {e}")
                continue

        logger.info(f"Processed {len(processed)}/{len(papers)} {domain} papers")
        logger.info(f"Unknown domains: {unknown_domains}, Unknown sections: {unknown_sections}")
        return processed

    def _save_intermediate(self, papers: List[Dict], filename: str) -> None:
        """
        Save intermediate results to disk as JSONL.

        Args:
            papers: List of paper/sample dictionaries.
            filename: Output filename.
        """
        path = self.data_dir / filename
        try:
            with open (path, "w", encoding="utf-8") as f:
                for paper in papers:
                    f.write (json.dumps (paper, ensure_ascii=False) + "\n")
            logger.info (f"Saved checkpoint to {path}")
        except (OSError, IOError, PermissionError) as e:
            logger.error (f"Failed to save intermediate file {filename}: {e}")
        except (TypeError, ValueError) as e:
            logger.error (f"JSON serialization error for {filename}: {e}")

    def build_corpus(self, output_path: str, verify_only: bool = False) -> None:
        """
        Build the complete scientific corpus with checkpoint verification.

        Args:
            output_path: Path to save the final corpus.
            verify_only: If True, only verify checkpoints and skip merging.
        """
        logger.info("Starting scientific corpus build...")
        total_start = time.time()
        all_papers = []

        sources = [
            ("arXiv", self.fetch_arxiv_papers, None),
            ("PubMed", self.fetch_pubmed_papers, "biology"),
            ("FineWeb-Edu", self.fetch_fineweb_edu, "education")
        ]
        for source_name, fetch_func, domain in sources:
            if is_shutdown:
                break
            logger.info(f"Fetching {source_name} papers...")
            try:
                papers = fetch_func()
                if domain:
                    processed = []
                    for i in range(0, len(papers), self.config.chunk_size):
                        chunk = papers[i:i + self.config.chunk_size]
                        processed.extend(self.process_papers(chunk, domain))
                    papers = processed
                chkpt_filename = f"{source_name.lower()}_papers.jsonl"
                self._save_intermediate(papers, chkpt_filename)
                if not papers:
                    logger.error(f"{source_name} checkpoint {chkpt_filename} is empty!")
                all_papers.extend(papers)
                logger.info(f"Added {len(papers)} papers from {source_name}")
            except Exception as e:
                logger.error(f"Critical error fetching from {source_name}: {e}")
                continue

        logger.info(f"Total papers collected: {len(all_papers)}")
        if verify_only:
            logger.info("Verification flag enabled; skipping merge and build.")
            self.print_report({})
            return

        if not all_papers:
            logger.error("No papers collected. Cannot build corpus.")
            self.print_report({})
            return

        logger.info("Ranking and deduplicating papers...")
        try:
            ranked_papers = self.ranker.rank_samples(all_papers)
            if not ranked_papers:
                logger.error("Final corpus is empty after ranking. Using unranked papers as fallback.")
                ranked_papers = all_papers
            logger.info(f"Final corpus size: {len(ranked_papers)} papers")
        except Exception as e:
            logger.error(f"Error ranking papers: {e}")
            ranked_papers = all_papers

        if not ranked_papers:
            logger.error("Final corpus is empty. No data to process or save.")
            self.print_report({})
            return

        self._save_intermediate(ranked_papers, "ranked_papers.jsonl")
        try:
            stats = self.analyzer.get_dataset_stats(ranked_papers)
            self.metrics["total_tokens"] = int(stats.get("avg_tokens", 0) * stats.get("total_samples", 0))
        except Exception as e:
            logger.error(f"Error generating dataset statistics: {e}")
            stats = {}

        self.metrics["total_time"] = time.time() - total_start
        logger.info("Processing final dataset in batches...")
        try:
            with open(output_path, "w", encoding="utf-8") as out_f:
                for i in range(0, len(ranked_papers), self.config.chunk_size):
                    chunk = ranked_papers[i:i + self.config.chunk_size]
                    for paper in chunk:
                        out_f.write(json.dumps(paper, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Error processing final dataset: {e}")

        # HuggingFace upload: warn if a file is too large
        if os.path.exists(output_path) and os.path.getsize(output_path) > 10 * 1024 * 1024:
            logger.warning(
                f"{output_path} is larger than 10 MiB. HuggingFace will reject files >10 MiB unless you use Git LFS. "
                "See https://hf.co/docs/hub/repositories-getting-started#terminal"
            )
            logger.warning(
                "To fix: install git-lfs and run 'git lfs track \"*.jsonl\"' before pushing, or split your file."
            )

        self.print_report(stats)
        logger.info(f"Scientific corpus successfully built: {output_path}")

    def print_report(self, stats: Dict) -> None:
        """
        Print a comprehensive build report.

        Args:
            stats: Dictionary of dataset statistics.
        """
        print("\n" + "=" * 67)
        print("           SCIENTIFIC CORPUS BUILD REPORT")
        print("=" * 67)
        print("\nSOURCE METRICS:")
        print("-" * 40)
        for source_name, label in zip(["arxiv", "pubmed", "fineweb_edu"],
                                      ["ARXIV", "PUBMED", "FINEWEB_EDU"]):
            metrics = self.metrics[source_name]
            print(f"{label:15}: {metrics.papers:6d} papers | {metrics.errors:3d} errors | {metrics.time:9.2f}s")
        print("\nOVERALL METRICS:")
        print("-" * 40)
        total_papers = sum(self.metrics[src].papers for src in ["arxiv", "pubmed", "fineweb_edu"])
        total_errors = sum(self.metrics[src].errors for src in ["arxiv", "pubmed", "fineweb_edu"])
        print(f"Total Papers:     {total_papers:,}")
        print(f"Total Tokens:     {self.metrics['total_tokens']:,}")
        print(f"Total Time:       {self.metrics['total_time']:.2f}s")
        print(f"Total Errors:     {total_errors}")
        success_rate = (1 - total_errors / max(total_papers + total_errors, 1)) * 100
        print(f"Success Rate:     {success_rate:.2f}%")
        if stats:
            print("\nDATASET STATISTICS:")
            print("-" * 40)
            for key, value in stats.items():
                print(f"{key:20}: {value}")
        print("=" * 67)
        print()


def main() -> None:
    """
    Main entry point for the corpus builder.
    """
    try:
        config = CorpusConfig()
        builder = ScientificCorpusBuilder(config)
        output_path = "scientific_corpus_325M.jsonl"
        builder.build_corpus(output_path)

        # --- Hugging Face upload with improved error handling ---
        try:
            # Split large files if needed
            file_size = os.path.getsize(output_path)
            if file_size > 10 * 1024 * 1024:  # 10 MB
                logger.info("Large file detected, splitting into chunks...")
                chunk_size = 10 * 1024 * 1024  # 10 MB chunks
                base_path = os.path.splitext(output_path)[0]
                
                with open(output_path, 'r', encoding='utf-8') as f:
                    chunk_num = 0
                    chunk = []
                    current_size = 0
                    
                    for line in f:
                        line_size = len(line.encode('utf-8'))
                        if current_size + line_size > chunk_size and chunk:
                            chunk_path = f"{base_path}_part{chunk_num}.jsonl"
                            with open(chunk_path, 'w', encoding='utf-8') as chunk_file:
                                chunk_file.writelines(chunk)
                            logger.info(f"Created chunk {chunk_num}: {chunk_path}")
                            chunk = []
                            current_size = 0
                            chunk_num += 1
                        
                        chunk.append(line)
                        current_size += line_size
                    
                    # Write final chunk
                    if chunk:
                        chunk_path = f"{base_path}_part{chunk_num}.jsonl"
                        with open(chunk_path, 'w', encoding='utf-8') as chunk_file:
                            chunk_file.writelines(chunk)
                        logger.info(f"Created final chunk {chunk_num}: {chunk_path}")
                
                # Upload each chunk
                for i in range(chunk_num + 1):
                    chunk_path = f"{base_path}_part{i}.jsonl"
                    logger.info(f"Uploading chunk {i}...")
                    upload_to_huggingface(
                        dataset_path=chunk_path,
                        repo_id="Allanatrix/Scientific_Research_Tokenized",
                        auto_generate_readme=(i == 0),  # Only generate README for first chunk
                        compress=True,
                        keep_local=True  # Keep files until all uploads complete
                    )
            else:
                # Upload single file
                upload_to_huggingface(
                    dataset_path=output_path,
                    repo_id="Allanatrix/Scientific_Research_Tokenized",
                    auto_generate_readme=True,
                    compress=True
                )
                
        except ImportError:
            logger.error("Hugging Face upload module not found. Please ensure hf_upload.py exists.")
        except Exception as e:
            logger.error(f"Error during Hugging Face upload: {e}")
            if "EOF" in str(e) or "timeout" in str(e):
                logger.warning("Upload interrupted. Try using smaller chunks or increasing timeout.")
        finally:
            # Cleanup temporary files
            if 'chunk_num' in locals():
                for i in range(chunk_num + 1):
                    try:
                        os.remove(f"{base_path}_part{i}.jsonl")
                    except OSError:
                        pass

    except KeyboardInterrupt:
        logger.info("Build process interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
        raise

if __name__ == "__main__":
    main()