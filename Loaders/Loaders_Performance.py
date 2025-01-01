import time
import psutil
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import List, Any
import logging
import numpy as np
from dataclasses import dataclass

# Configure logging
logging.basicConfig (level=logging.INFO)
logger = logging.getLogger (__name__)


@dataclass
class PerformanceMetric:
    """Data class to store performance metrics"""
    loader_name: str
    time_taken: float
    memory_used: float
    cpu_percent: float
    throughput: float
    data_size: int


def _measure_performance(loader) -> PerformanceMetric:
    """Measure the performance of a data loader."""
    start_time = time.time ()
    process = psutil.Process ()
    start_memory = process.memory_info ().rss
    start_cpu = process.cpu_percent (interval=None)

    # Load data
    data = loader.load_data ()
    data_size = len (data)

    end_time = time.time ()
    end_memory = process.memory_info ().rss
    end_cpu = process.cpu_percent (interval=None)

    time_taken = end_time - start_time
    memory_used = (end_memory - start_memory) / (1024 * 1024)  # Convert to MB
    cpu_percent = end_cpu - start_cpu
    throughput = data_size / time_taken if time_taken > 0 else 0

    return PerformanceMetric (
        loader_name=loader.__class__.__name__,
        time_taken=time_taken,
        memory_used=memory_used,
        cpu_percent=cpu_percent,
        throughput=throughput,
        data_size=data_size
    )


class PerformanceMonitor:
    """Monitor and visualize loader performance"""

    def __init__(self, loaders: List [Any], num_runs: int = 3):
        self.loaders = loaders
        self.num_runs = num_runs
        self.metrics: List [PerformanceMetric] = []

        # Set up plot style
        sns.set_style ("whitegrid")
        sns.set_palette ("husl")

    def run_benchmarks(self) -> None:
        """Run performance benchmarks for all loaders"""
        for loader in self.loaders:
            logger.info (f"Benchmarking {loader.__class__.__name__}")

            # Run multiple times and average
            run_metrics = []
            for run in range (self.num_runs):
                try:
                    metric = _measure_performance (loader)
                    run_metrics.append (metric)
                    logger.info (f"Run {run + 1}: Time={metric.time_taken:.2f}s, Memory={metric.memory_used:.2f}MB")
                except Exception as e:
                    logger.error (f"Error in run {run + 1} for {loader.__class__.__name__}: {str (e)}")

            # Average the metrics
            if run_metrics:
                avg_metric = PerformanceMetric (
                    loader_name=loader.__class__.__name__,
                    time_taken=np.mean ([m.time_taken for m in run_metrics]),
                    memory_used=np.mean ([m.memory_used for m in run_metrics]),
                    cpu_percent=np.mean ([m.cpu_percent for m in run_metrics]),
                    throughput=np.mean ([m.throughput for m in run_metrics]),
                    data_size=run_metrics [0].data_size
                )
                self.metrics.append (avg_metric)

    def plot_metrics(self, save_path: str = None) -> None:
        """Create enhanced visualizations of performance metrics"""
        if not self.metrics:
            logger.error("No metrics to plot. Run benchmarks first.")
            return

        # Convert metrics to DataFrame for easier plotting
        df = pd.DataFrame([vars(m) for m in self.metrics])

        # Create a figure with subplots
        fig, axs = plt.subplots(1, 2, figsize=(18, 7))
        fig.suptitle('Loader Performance Metrics', fontsize=20, y=1.05)

        # Time and Memory subplot
        ax1 = axs[0]
        time_bars = ax1.bar(df['loader_name'], df['time_taken'], color='skyblue')
        ax1.set_ylabel('Time (s)', color='skyblue', fontsize=12)
        ax1.tick_params(axis='y', labelcolor='skyblue')
        ax1.set_title('Time Taken', fontsize=14)

        ax2 = ax1.twinx()
        memory_line = ax2.plot(df['loader_name'], df['memory_used'], 'r-o', label='Memory Usage')
        ax2.set_ylabel('Memory (MB)', color='red', fontsize=12)
        ax2.tick_params(axis='y', labelcolor='red')

        # Throughput subplot
        ax3 = axs[1]
        sns.barplot(data=df, x='loader_name', y='throughput', ax=ax3, color='purple')
        ax3.set_ylabel('Records per Second', fontsize=12)
        ax3.set_title('Data Loading Throughput', fontsize=14)

        # Adjust tick labels
        ax3.set_xticks(range(len(df['loader_name'])))
        ax3.set_xticklabels(df['loader_name'], rotation=45, ha='right')

        plt.tight_layout(rect=[0, 0, 1, 0.96])

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')

        plt.show()

    def generate_report(self) -> str:
        """Generate a performance report"""
        if not self.metrics:
            return "No metrics available. Run benchmarks first."

        report = ["Performance Benchmark Report", "=" * 30, ""]

        for metric in self.metrics:
            report.extend ([
                f"\nLoader: {metric.loader_name}",
                f"Time Taken: {metric.time_taken:.2f} seconds",
                f"Memory Used: {metric.memory_used:.2f} MB",
                f"CPU Usage: {metric.cpu_percent:.1f}%",
                f"Throughput: {metric.throughput:.0f} records/second",
                f"Data Size: {metric.data_size:,} records",
                "-" * 30
            ])

        return "\n".join (report)


# Example usage
if __name__ == "__main__":
    from Loaders.csv_loader import CSVLoader
    from Loaders.sql_loader import SQLLoader
    from Loaders.s3_loader import S3Loader

    # Initialize loaders
    loaders = [
        CSVLoader (file_path="C:/Users/kunya/PycharmProjects/DataStream/data/customers-10000.csv"),
        # SQLLoader (connection_string="your_connection_string", query="SELECT * FROM your_table"),
        # S3Loader (bucket_name="your_bucket", file_key="your_file_key")
    ]

    # Create and run performance monitor
    monitor = PerformanceMonitor (loaders, num_runs=3)
    monitor.run_benchmarks ()

    # Generate visualizations and report
    monitor.plot_metrics (save_path="loader_performance.png")
    print (monitor.generate_report ())
