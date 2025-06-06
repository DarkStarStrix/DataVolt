import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from datasets import Dataset
from huggingface_hub import HfApi, Repository, create_repo
import getpass

# Setup detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('upload_log.txt')
    ]
)

def check_file_size(file_path):
    """Check file size and warn if too large"""
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    logging.info(f"File size: {size_mb:.2f} MB")
    if size_mb > 10:
        logging.warning(f"File is larger than 10MB. Setting up Git LFS...")
        return True
    return False

def setup_git_lfs(repo_dir):
    """Setup Git LFS for large files (no global chdir)"""
    try:
        subprocess.run("git lfs install", shell=True, check=True, cwd=repo_dir)
        subprocess.run('git lfs track "*.arrow"', shell=True, check=True, cwd=repo_dir)
        subprocess.run('git lfs track "*.jsonl"', shell=True, check=True, cwd=repo_dir)
        subprocess.run("git add .gitattributes", shell=True, check=True, cwd=repo_dir)
        logging.info("Git LFS setup successful")
        # Print .gitattributes for debug
        gitattributes = Path(repo_dir) / ".gitattributes"
        if gitattributes.exists():
            with open(gitattributes, "r") as f:
                logging.info(f".gitattributes:\n{f.read()}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Git LFS setup failed: {e}")
        raise

def write_readme(repo_dir, num_rows):
    """Write a simple README.md to the repo directory."""
    readme_path = Path(repo_dir) / "README.md"
    content = f"""# Scientific Research Tokenized

This dataset contains {num_rows} examples of scientific research text, tokenized and compressed for efficient ML training.

- Source: scientific_corpus_325M.jsonl
- Format: Arrow, JSONL

Uploaded and versioned via script.
"""
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)
    logging.info("README.md written.")

def upload_dataset(jsonl_path, repo_id, token):
    repo_dir = Path("Scientific_Research_Tokenized")
    try:
        # Remove repo_dir if it exists to ensure a clean clone
        if repo_dir.exists():
            logging.info("Removing existing repo directory for a clean clone.")
            import shutil
            shutil.rmtree(repo_dir)
        # 1. Create a repository if it doesn't exist
        HfApi()
        create_repo(repo_id, repo_type="dataset", token=token, exist_ok=True)
        logging.info(f"Repository ready: {repo_id}")

        # 2. Setup repository
        repo = Repository(
            local_dir=str(repo_dir),
            clone_from=f"https://huggingface.co/datasets/{repo_id}",
            use_auth_token=token,
            git_user="Allanatrix",
            git_email="allanw.mk@gmail.com"
        )
        logging.info("Repository cloned successfully")

        # 3. Setup Git LFS if needed
        if check_file_size(jsonl_path):
            setup_git_lfs(repo_dir)

        # 4. Copy JSONL into repo dir
        dest_jsonl = repo_dir / Path(jsonl_path).name
        if not dest_jsonl.exists():
            import shutil
            shutil.copy2(jsonl_path, dest_jsonl)
            logging.info(f"Copied {jsonl_path} to {dest_jsonl}")

        # 5. Convert to Arrow format with progress
        logging.info("Converting to Arrow format...")
        try:
            ds = Dataset.from_json(str(dest_jsonl))
            arrow_path = repo_dir / "scientific_corpus_325M.arrow"
            ds.save_to_disk(str(arrow_path), max_shard_size="500MB")
            logging.info(f"Arrow conversion successful: {arrow_path}")
        except Exception as e:
            logging.error(f"Arrow conversion failed: {e}")
            raise

        # Write README
        write_readme(repo_dir, len(ds))

        # 6. Add, commit, and push
        logging.info("Pushing to Hugging Face...")
        max_retries = 3
        for attempt in range(max_retries):
            try:
                repo.git_add(".")
                repo.git_commit(f"Upload dataset {datetime.now().isoformat()}")
                # Debug: print git status and log
                subprocess.run("git status", shell=True, cwd=repo_dir)
                subprocess.run("git log -2", shell=True, cwd=repo_dir)
                repo.git_push()
                logging.info("Push successful!")
                return True
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 30
                    logging.warning(f"Push attempt {attempt + 1} failed. Retrying in {wait_time} seconds...")
                    logging.error(f"Error details: {str(e)}")
                    time.sleep(wait_time)
                else:
                    logging.error(f"Final push attempt failed: {e}")
                    # Print last git status/log for debugging
                    subprocess.run("git status", shell=True, cwd=repo_dir)
                    subprocess.run("git log -2", shell=True, cwd=repo_dir)
                    raise
        return None

    except Exception as e:
        logging.error(f"Upload failed: {str(e)}")
        return False

def get_hf_token():
    """Prompt user for Hugging Face token (hidden input)."""
    print("\nPlease enter your Hugging Face token (input will be hidden):")
    print("You can create or copy a token from https://huggingface.co/settings/tokens")
    token = getpass.getpass("Token: ").strip()
    if not token:
        logging.error("No token entered. Exiting.")
        sys.exit(1)
    return token


def validate_token(token):
    """Validate Hugging Face token"""
    if not token:
        logging.error("Hugging Face token is not set.")
        return False
    try:
        api = HfApi()
        api.whoami(token=token)
        logging.info("Hugging Face token is valid.")
        return True
    except Exception as e:
        logging.error(f"Invalid Hugging Face token: {e}")
        return False


if __name__ == "__main__":
    try:
        # Get and validate token
        token = get_hf_token()
        if not validate_token(token):
            sys.exit(1)

        # Configure paths
        jsonl_path = Path(r"C:\Users\kunya\PycharmProjects\DataVolt\Tokenization\scientific_corpus_325M.jsonl")
        repo_id = "Allanatrix/Scientific_Research_Tokenized"

        # Start upload with progress tracking
        logging.info("=== Starting Upload Process ===")
        success = upload_dataset(jsonl_path, repo_id, token)
        
        if success:
            logging.info("=== Upload Complete ===")
            logging.info(f"Dataset available at: https://huggingface.co/datasets/{repo_id}")
        else:
            logging.error("Upload failed. Check upload_log.txt for details.")
            sys.exit(1)

    except KeyboardInterrupt:
        logging.info("\nUpload cancelled by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        sys.exit(1)