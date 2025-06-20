import os
import uuid
from Nexa_Backend.Tokenization.generate_dataset import generate_dataset as backend_generate_dataset

DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), '../static/downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def generate_corpus(source, num_tokens, plan='free', session_id=None):
    """
    Wrapper for scientific corpus generation. Returns a path to .jsonl file.
    """
    session_id = session_id or str(uuid.uuid4())
    out_path = os.path.join(DOWNLOAD_DIR, f"corpus_{session_id}.jsonl")
    # Call backend pipeline (simulate for now)
    result = backend_generate_dataset(domain=source, token_budget=num_tokens, plan=plan, job_type="corpus")
    with open(out_path, "w", encoding="utf-8") as f:
        for line in result["jsonl_lines"]:
            f.write(line + "\n")
    return out_path

