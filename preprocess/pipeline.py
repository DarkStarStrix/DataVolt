import pandas as pd
import logging
from typing import List
import time
import psutil
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger (__name__)


def _monitor_resources() -> dict:
    """Monitor system resources"""
    cpu_percent = psutil.cpu_percent (interval=0.1)
    memory = psutil.virtual_memory ()
    return {
        'cpu_percent': cpu_percent,
        'memory_percent': memory.percent,
        'memory_used_gb': memory.used / (1024 ** 3)
    }


class PreprocessingPipeline:
    """Memory-aware preprocessing a pipeline with performance monitoring"""

    def __init__(self, steps: List):
        self.steps = steps
        self.num_workers = 7

    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        """Process data through a pipeline with resource monitoring"""
        start_time = time.perf_counter ()
        initial_memory = psutil.virtual_memory ().used / (1024 ** 3)

        logger.info (f"Starting pipeline processing with shape: {data.shape}")

        try:
            for step in self.steps:
                step_start = time.perf_counter ()
                resources_before = _monitor_resources ()

                # Process data
                data = step.transform (data)

                resources_after = _monitor_resources ()
                step_end = time.perf_counter ()

                # Log performance metrics
                logger.info (f"""
                    {step.__class__.__name__} completed:
                    Time: {step_end - step_start:.2f} seconds
                    CPU Usage: {resources_after ['cpu_percent']}%
                    Memory Usage: {resources_after ['memory_used_gb']:.2f} GB
                    Memory Change: {resources_after ['memory_used_gb'] - resources_before ['memory_used_gb']:.2f} GB
                """)

            end_time = time.perf_counter ()
            final_memory = psutil.virtual_memory ().used / (1024 ** 3)

            logger.info (f"""
                Pipeline completed:
                Total time: {end_time - start_time:.2f} seconds
                Total memory change: {final_memory - initial_memory:.2f} GB
                Final shape: {data.shape}
            """)

            return data

        except Exception as e:
            logger.error (f"Pipeline error: {str (e)}")
            raise
