import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import logging
from typing import Optional, List
import os
import psutil

logger = logging.getLogger (__name__)


def _process_chunk(chunk: pd.DataFrame) -> pd.DataFrame:
    """Process a single chunk of data"""
    # Optimize dtypes
    for column in chunk.columns:
        if chunk [column].dtype == 'object':
            # Convert string columns to categorical
            if chunk [column].nunique () / len (chunk) < 0.5:  # If less than 50% unique values
                chunk [column] = chunk [column].astype ('category')
        elif chunk [column].dtype == 'float64':
            # Downcast float64 to float32 if possible
            chunk [column] = pd.to_numeric (chunk [column], downcast='float')
        elif chunk [column].dtype == 'int64':
            # Downcast int64 to the smallest possible int type
            chunk [column] = pd.to_numeric (chunk [column], downcast='integer')

    return chunk


class CSVLoader:
    """Optimized CSV loader using multiple cores and memory-aware chunking"""

    def __init__(self, file_path: str):
        self.file_path = Path (file_path)
        # Calculate optimal chunk size based on available memory
        total_ram = psutil.virtual_memory ().total / (1024 * 1024 * 1024)  # GB
        self.reserved_ram = 2  # Reserve 2GB for a system and other processes
        self.available_ram = total_ram - self.reserved_ram
        self.num_workers = 7  # Using 7 cores, leaving 1 for system processes

    def _calculate_chunk_size(self, file_size: int) -> int:
        """Calculate optimal chunk size based on available RAM"""
        # Estimate 1.5x file size for DataFrame memory usage
        estimated_df_size = file_size * 1.5 / (1024 * 1024 * 1024)  # GB
        if estimated_df_size < self.available_ram:
            return 0  # Load a full file
        else:
            # Calculate chunks to fit in 1/4 of available RAM
            chunk_size = int ((self.available_ram * 0.25 * 1024 * 1024) / estimated_df_size)
            return max (1000, chunk_size)  # Minimum 1000 rows per chunk

    def load_data(self) -> pd.DataFrame:
        """Load CSV data with optimal memory usage and parallel processing"""
        try:
            file_size = os.path.getsize (self.file_path)
            chunk_size = self._calculate_chunk_size (file_size)

            logger.info (f"Loading CSV with chunk size: {chunk_size if chunk_size > 0 else 'Full file'}")

            if chunk_size == 0:
                # Load an entire file if it fits in memory
                df = pd.read_csv (self.file_path)
                return _process_chunk (df)

            chunks: List [pd.DataFrame] = []
            reader = pd.read_csv (self.file_path, chunksize=chunk_size)

            # Process chunks in parallel
            with ThreadPoolExecutor (max_workers=self.num_workers) as executor:
                chunks = list (executor.map (_process_chunk, reader))

            # Combine chunks efficiently
            final_df = pd.concat (chunks, ignore_index=True)

            logger.info (f"Successfully loaded data with shape: {final_df.shape}")
            return final_df

        except Exception as e:
            logger.error (f"Error loading CSV: {str (e)}")
            raise
