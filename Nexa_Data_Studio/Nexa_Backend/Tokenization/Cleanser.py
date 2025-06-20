import json
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datasets import Dataset

# Tag dictionaries
DOMAIN_TAGS = {
    "physics": "[PHYS]",
    "biology": "[BIO]",
    "materials": "[MAT]",
    "education": "[GEN]",
}

TASK_TAGS = {
    "hypothesis": "[HYP]",
    "method": "[MTH]",
    "experiment": "[EXP]",
}

SECTION_TAGS = {
    "abstract": "[ABSTRACT]",
    "introduction": "[INTRO]",
    "results": "[RESULTS]",
    "discussion": "[DISCUSSION]",
    "conclusion": "[CONCLUSION]",
    "method": "[MTH]",
    "experiment": "[EXP]",
}

SRC_PATH = Path(r"C:\Users\kunya\PycharmProjects\DataVolt\Tokenization\scientific_corpus_325M.jsonl")
CLEANED_JSONL_PATH = Path("scientific_corpus_325M.cleaned.jsonl")
CLEANED_ARROW_PATH = Path("scientific_corpus_325M.cleaned.arrow")
CHUNK_SIZE = 10000
MAX_WORKERS = os.cpu_count() or 4

def tag_record(record):
    # Tagging logic: add tags to text fields if domain/task/section present
    # You may need to adjust keys based on your schema
    domain = record.get("domain", "").lower()
    task = record.get("task", "").lower()
    section = record.get("section", "").lower()
    text = record.get("full_text", "")

    tags = []
    if domain in DOMAIN_TAGS:
        tags.append(DOMAIN_TAGS[domain])
    if task in TASK_TAGS:
        tags.append(TASK_TAGS[task])
    if section in SECTION_TAGS:
        tags.append(SECTION_TAGS[section])

    # Prepend tags to text
    record["tagged_text"] = " ".join(tags) + " " + text if tags else text
    return record

def process_chunk(lines):
    cleaned = []
    for line in lines:
        try:
            record = json.loads(line)
            cleaned.append(tag_record(record))
        except Exception:
            continue  # skip malformed lines
    return cleaned

def chunked_file_reader(path, chunk_size):
    with open(path, "r", encoding="utf-8") as f:
        chunk = []
        for line in f:
            chunk.append(line)
            if len(chunk) == chunk_size:
                yield chunk
                chunk = []
        if chunk:
            yield chunk

def main():
    print("Starting cleaning process...")
    # Write cleaned records to a new JSONL file in chunks
    with open(CLEANED_JSONL_PATH, "w", encoding="utf-8") as out_f:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = []
            for chunk in chunked_file_reader(SRC_PATH, CHUNK_SIZE):
                futures.append(executor.submit(process_chunk, chunk))
            for fut in as_completed(futures):
                for record in fut.result():
                    out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"Cleaned JSONL written to {CLEANED_JSONL_PATH}")

    # Convert cleaned JSONL to Arrow using datasets (handles chunking internally)
    print("Saving cleaned dataset to Arrow format...")
    ds = Dataset.from_json(str(CLEANED_JSONL_PATH))
    ds.save_to_disk(str(CLEANED_ARROW_PATH))
    print(f"Saved cleaned Arrow dataset at: {CLEANED_ARROW_PATH}")

    # Optionally, call hf_upload.py asynchronously
    print("Uploading to HuggingFace using hf_upload.py ...")
    os.system(f"python hf_upload.py")

if __name__ == "__main__":
    main()