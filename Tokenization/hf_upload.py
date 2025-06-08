import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from datasets import Dataset, Features, Value
from dotenv import load_dotenv
from huggingface_hub import HfApi

# Load environment variables
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('debug_upload.log', mode='w')
    ]
)

REPO_ID = "Allanatrix/Scientific_Research_Tokenized"
JSONL_SRC = Path(r"C:\Users\kunya\PycharmProjects\DataVolt\Tokenization\scientific_corpus_325M.jsonl")
ARROW_PATH = Path("scientific_corpus_325M.arrow")
README_PATH = Path("README.md")

def debug_jsonl_head(jsonl_path, n=5):
    logging.info(f"Printing the first {n} lines of {jsonl_path} for schema inspection:")
    try:
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for i in range(n):
                line = f.readline()
                if not line:
                    break
                logging.info(f"Line {i+1}: {line.strip()}")
    except Exception as e:
        logging.error(f"Failed to read JSONL head: {e}")

def infer_features_from_sample(jsonl_path, n=100):
    import json
    from collections import defaultdict
    types = defaultdict(set)
    try:
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i >= n:
                    break
                obj = json.loads(line)
                for k, v in obj.items():
                    types[k].add(type(v).__name__)
        logging.info(f"Inferred field types from first {n} lines: {dict(types)}")
    except Exception as e:
        logging.error(f"Failed to infer features: {e}")

def convert_jsonl_to_arrow(jsonl_path, arrow_path):
    try:
        logging.info(f"Converting {jsonl_path} to Arrow format at {arrow_path} ...")
        if not jsonl_path.exists():
            logging.error(f"JSONL source file does not exist: {jsonl_path}")
            print(f"\n❌ JSONL source file does not exist: {jsonl_path}")
            raise FileNotFoundError(f"JSONL source file does not exist: {jsonl_path}")
        logging.info(f"File size: {jsonl_path.stat().st_size} bytes")
        debug_jsonl_head(jsonl_path, n=5)
        infer_features_from_sample(jsonl_path, n=100)
        # Try loading a small sample first for debugging
        try:
            sample_dataset = Dataset.from_json(str(jsonl_path), split="train[:1000]")
            logging.info(f"Sample loaded: {len(sample_dataset)} rows, columns: {sample_dataset.column_names}")
        except Exception as sample_e:
            logging.error(f"Failed to load sample from JSONL: {sample_e}", exc_info=True)
            print(f"\n❌ Failed to load sample from JSONL. See debug_upload.log for details.")
            # Try to load with explicit features if possible
            # Example: features = Features({'url': Value('string'), 'pubmed_id': Value('string')})
            # Uncomment and adjust the following lines if you know the schema:
            # features = Features({'url': Value('string'), 'pubmed_id': Value('string')})
            # try:
            #     sample_dataset = Dataset.from_json(str(jsonl_path), split="train[:1000]", features=features)
            #     logging.info(f"Sample loaded with explicit features: {len(sample_dataset)} rows, columns: {sample_dataset.column_names}")
            # except Exception as e2:
            #     logging.error(f"Still failed with explicit features: {e2}", exc_info=True)
            raise
        # Now load the full dataset
        dataset = Dataset.from_json(str(jsonl_path))
        logging.info(f"Full dataset loaded: {len(dataset)} rows, columns: {dataset.column_names}")
        dataset.to_file(str(arrow_path))
        logging.info(f"Saved Arrow dataset with {len(dataset):,} rows.")
        return dataset
    except Exception as e:
        logging.error(f"An error occurred while generating the dataset: {e}", exc_info=True)
        print(f"\n❌ Failed to convert JSONL to Arrow. See debug_upload.log for details.")
        raise

def create_readme(dataset):
    content = f"""# Scientific Research Tokenized Dataset

- **Examples**: {len(dataset):,}
- **Columns**: {dataset.column_names}
- **Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Usage
```python
from datasets import load_dataset
ds = load_dataset("{REPO_ID}")
```
"""
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    logging.info("README.md created.")

def upload_to_hf():
    api = HfApi()
    logging.info("Uploading Arrow file to HuggingFace Hub ...")
    api.upload_file(
        path_or_fileobj=str(ARROW_PATH),
        path_in_repo=ARROW_PATH.name,
        repo_id=REPO_ID,
        repo_type="dataset",
        token=HF_TOKEN,
        commit_message="Upload Arrow dataset"
    )
    logging.info("Uploading README.md to HuggingFace Hub ...")
    api.upload_file(
        path_or_fileobj=str(README_PATH),
        path_in_repo="README.md",
        repo_id=REPO_ID,
        repo_type="dataset",
        token=HF_TOKEN,
        commit_message="Update README"
    )
    logging.info("Upload complete.")

def cleanup():
    if ARROW_PATH.exists():
        ARROW_PATH.unlink()
    if README_PATH.exists():
        README_PATH.unlink()
    logging.info("Cleaned up local files.")

def main():
    try:
        if not HF_TOKEN:
            print("❌ HF_TOKEN not found in environment. Please set it in your .env file.")
            return
        dataset = convert_jsonl_to_arrow(JSONL_SRC, ARROW_PATH)
        create_readme(dataset)
        upload_to_hf()
        print(f"\n🎉 SUCCESS! View at: https://huggingface.co/datasets/{REPO_ID}")
    except Exception as e:
        logging.error(f"Process failed: {e}")
        print(f"\n❌ Upload failed. See debug_upload.log for details.")
        sys.exit(1)
    finally:
        cleanup()

if __name__ == "__main__":
    main()