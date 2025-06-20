import os
import shutil

def save_file_to_downloads(src_path, session_id, filename=None):
    """
    Move or copy a file to the static/downloads/session_id/ folder.
    Returns the new path.
    """
    downloads_dir = os.path.join(os.path.dirname(__file__), '../static/downloads', session_id)
    os.makedirs(downloads_dir, exist_ok=True)
    dest = os.path.join(downloads_dir, filename or os.path.basename(src_path))
    shutil.copy2(src_path, dest)
    return dest
