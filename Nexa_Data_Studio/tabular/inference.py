import os
import uuid
import csv

def generate_tabular(domain, num_rows, session_id=None):
    """
    Simulate tabular data generation. Returns path to .csv file.
    """
    session_id = session_id or str(uuid.uuid4())
    out_path = os.path.join(os.path.dirname(__file__), f"../static/downloads/tabular_{domain}_{session_id}.csv")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    # Simulate data
    header = ["feature1", "feature2", "feature3"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for i in range(num_rows):
            writer.writerow([f"{domain}_val1_{i}", f"{domain}_val2_{i}", f"{domain}_val3_{i}"])
    return out_path
