import pandas as pd
from mp_api.client import MPRester
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import shutil
import tempfile

API_KEY = ""
MAX_WORKERS = 4
CHUNK_SIZE = 50


def create_directory(path):
    """Create directory if it doesn't exist"""
    if not os.path.exists (path):
        os.makedirs (path)


def download_cif(args):
    """Download a single CIF file"""
    material_id, mpr = args
    try:
        # Create a temporary file path
        temp_dir = tempfile.gettempdir ()
        temp_path = os.path.join (temp_dir, f"{material_id}.cif")

        # Skip if a final file exists
        final_path = f"cif_files/{material_id}.cif"
        if os.path.exists (final_path):
            return None

        # Get structure and save CIF
        structure = mpr.get_structure_by_material_id (material_id)
        cif_string = structure.to (fmt="cif")

        with open (temp_path, "w") as f:
            f.write (cif_string)

        return temp_path, final_path

    except Exception as e:
        print (f"Error processing {material_id}: {str (e)}")
        return None


def batch_download_cifs(material_ids):
    """Download CIF files in parallel"""
    create_directory ("cif_files")

    # Create MPRester instances for each worker
    mpr_instances = [MPRester (API_KEY) for _ in range (MAX_WORKERS)]

    # Prepare download arguments
    download_args = [(mid, mpr) for mid, mpr in zip (material_ids,
                                                     [mpr_instances [i % MAX_WORKERS] for i in
                                                      range (len (material_ids))])]

    successful = 0
    failed = 0

    with ThreadPoolExecutor (max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit (download_cif, args) for args in download_args]

        for future in tqdm (as_completed (futures), total=len (futures), desc="Downloading CIFs"):
            result = future.result ()
            if result:
                temp_path, final_path = result
                # Move file from temp to final location
                shutil.move (temp_path, final_path)
                successful += 1
            else:
                failed += 1

    # Clean up MPRester instances
    for mpr in mpr_instances:
        mpr.close ()

    return successful, failed


def main():
    try:
        # Load materials dataset
        df = pd.read_csv ("lithium_battery_materials.csv")
        material_ids = df ["material_id"].tolist ()

        # Process in chunks for better memory management
        chunks = [material_ids [i:i + CHUNK_SIZE]
                  for i in range (0, len (material_ids), CHUNK_SIZE)]

        total_successful = 0
        total_failed = 0

        for chunk in tqdm (chunks, desc="Processing chunks"):
            successful, failed = batch_download_cifs (chunk)
            total_successful += successful
            total_failed += failed

        print ("\n✅ Download Summary:")
        print (f"Successfully downloaded: {total_successful}")
        print (f"Failed downloads: {total_failed}")
        print (f"Total materials processed: {total_successful + total_failed}")
        print (f"\nCIF files saved to: {os.path.abspath ('cif_files')}")

    except Exception as e:
        print (f"❌ Error: {str (e)}")


if __name__ == "__main__":
    main ()
