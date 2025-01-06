# preprocess/scaling.py

import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from typing import Dict
import logging
from numba import jit

logger = logging.getLogger (__name__)


class Scaler:
    """Memory-efficient parallel data scaler"""

    def __init__(self, method: str = None):
        self.method = method
        self.num_workers = 7
        self.scalers: Dict = {}

    @staticmethod
    @jit (nopython=True)
    def _minmax_scale_numba(arr: np.ndarray) -> np.ndarray:
        """JIT-compiled MinMax scaling"""
        min_val = np.min (arr)
        max_val = np.max (arr)
        if max_val > min_val:
            return (arr - min_val) / (max_val - min_val + 1e-8)
        return arr  # Return the original array if min_val equals max_val

    @staticmethod
    @jit (nopython=True)
    def _standard_scale_numba(arr: np.ndarray) -> np.ndarray:
        """JIT-compiled Standard scaling"""
        mean = np.mean (arr)
        std = np.std (arr)
        if std > 0:
            return (arr - mean) / std
        return arr - mean

    def _scale_column(self, data: pd.Series) -> pd.Series:
        """Scale a single column"""
        if self.method == 'minmax':
            scaled_values = self._minmax_scale_numba (data.values)
        elif self.method == 'standard':
            scaled_values = self._standard_scale_numba (data.values)
        else:
            raise ValueError (f"Unknown scaling method: {self.method}")
        return pd.Series (scaled_values, index=data.index, name=data.name)

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform data with parallel scaling"""
        result = data.copy ()
        numeric_cols = result.select_dtypes (include=['int64', 'float64']).columns

        if len (numeric_cols) > 0:
            # Process columns in parallel
            with ThreadPoolExecutor (max_workers=self.num_workers) as executor:
                scaled_cols = list (executor.map (
                    lambda col: self._scale_column (result [col]),
                    numeric_cols
                ))

                for col, scaled_data in zip (numeric_cols, scaled_cols):
                    result [col] = scaled_data

        logger.info (f"Scaled {len (numeric_cols)} numeric columns")
        return result
