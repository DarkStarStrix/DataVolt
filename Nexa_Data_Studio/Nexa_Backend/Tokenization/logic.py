import json
from datasets import Dataset
from pathlib import Path

JSONL_SRC = Path(r"C:\Users\kunya\PycharmProjects\DataVolt\Tokenization\scientific_corpus_325M.jsonl")

def count_lines(jsonl_path):
    with open(jsonl_path, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)

def check_jsonl_integrity(jsonl_path, max_lines=100000):
    print(f"Checking JSONL file: {jsonl_path}")
    error_line = None
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            try:
                json.loads(line)
            except Exception as e:
                print(f"Error parsing line {i}: {e}")
                print(f"Line content: {line[:200]}")
                error_line = i
                break
            if i % 10000 == 0:
                print(f"Checked {i} lines...")
            if i >= max_lines:
                print(f"Stopped after {max_lines} lines (no errors found).")
                break
    if not error_line:
        print("JSONL integrity check complete.")
    return error_line

def try_load_dataset_chunk(jsonl_path, start=0, stop=1000):
    print(f"Trying to load lines {start} to {stop} as a dataset...")
    split = f"train[{start}:{stop}]"
    try:
        ds = Dataset.from_json(str(jsonl_path), split=split)
        print(f"Loaded {len(ds)} rows. Columns: {ds.column_names}")
        return True
    except Exception as e:
        print(f"Failed to load chunk {start}:{stop}: {e}")
        # Try to load each line individually to find the problematic one
        for i in range(start, stop):
            try:
                Dataset.from_json (str (jsonl_path), split=f"train[{i}:{i + 1}]")
            except Exception as e2:
                print(f"❌ Failed to load line {i}: {e2}")
                with open(jsonl_path, "r", encoding="utf-8") as f:
                    for j, line in enumerate(f):
                        if j == i:
                            print(f"Line {i}: {line[:200]}")
                            break
                break
        return False

if __name__ == "__main__":
    total_lines = count_lines(JSONL_SRC)
    print(f"Total lines in file: {total_lines}")
    # Step 1: Check for JSON parse errors
    error_line = check_jsonl_integrity(JSONL_SRC, max_lines=500000)
    if error_line:
        print(f"First JSON parse error at line {error_line}.")
    else:
        # Step 2: Try loading in chunks to find where it fails
        chunk_size = 10000
        for start in range(0, min(100000, total_lines), chunk_size):
            stop = min(start + chunk_size, total_lines)
            ok = try_load_dataset_chunk(JSONL_SRC, start, stop)
            if not ok:
                print(f"Stopped at chunk {start}:{stop} due to error.")
                break
