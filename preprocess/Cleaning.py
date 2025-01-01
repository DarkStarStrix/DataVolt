import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List
import logging
from numba import jit
import psutil

logger = logging.getLogger (__name__)


def _clean_categorical_column(data: pd.Series) -> pd.Series:
    """Clean a categorical column with missing values"""
    if data.isnull ().any ():
        return data.fillna (data.mode ().iloc [0])
    return data


class DataCleaner:
    """Memory-efficient data cleaner with parallel processing"""

    def __init__(self, missing_value_strategy: str = 'fill'):
        self.strategy = missing_value_strategy
        self.fill_values: Dict = {}
        self.num_workers = 7  # Using 7 cores
        self.chunk_size = int (psutil.virtual_memory ().available * 0.1)  # Use 10% of available memory

    @staticmethod
    @jit (nopython=True)
    def _clean_numeric_array(arr: np.ndarray, fill_value: float) -> np.ndarray:
        """JIT-compiled numeric array cleaning"""
        return np.where (np.isnan (arr), fill_value, arr)

    def _clean_numeric_column(self, data: pd.Series) -> pd.Series:
        """Clean a numeric column with missing values"""
        if data.isnull ().any ():
            fill_value = data.mean ()
            return pd.Series (
                self._clean_numeric_array (data.values, fill_value),
                index=data.index,
                name=data.name
            )
        return data

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform data with parallel processing and memory efficiency"""
        result = data.copy ()

        # Split columns by type
        numeric_cols = result.select_dtypes (include=['int64', 'float64']).columns
        categorical_cols = result.select_dtypes (include=['object', 'category']).columns

        # Process numeric columns in parallel
        if len (numeric_cols) > 0:
            with ThreadPoolExecutor (max_workers=self.num_workers) as executor:
                numeric_results = list (executor.map (
                    lambda col: self._clean_numeric_column (result [col]),
                    numeric_cols
                ))
                for col, cleaned_data in zip (numeric_cols, numeric_results):
                    result [col] = cleaned_data

        # Process categorical columns in parallel
        if len (categorical_cols) > 0:
            with ThreadPoolExecutor (max_workers=self.num_workers) as executor:
                categorical_results = list (executor.map (
                    lambda col: _clean_categorical_column (result [col]),
                    categorical_cols
                ))
                for col, cleaned_data in zip (categorical_cols, categorical_results):
                    result [col] = cleaned_data

        # Remove duplicates efficiently
        result.drop_duplicates (inplace=True)

        logger.info (f"Cleaned data shape: {result.shape}")
        return result
