import time
import psutil
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import List, Any, Optional
import logging
import numpy as np
from dataclasses import dataclass
from matplotlib.gridspec import GridSpec

# Configure logging with a more detailed format
logging.basicConfig (
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
    """Enhanced monitor and visualize loader performance"""

    def __init__(self, loaders: List [Any], num_runs: int = 3):
        self.loaders = loaders
        self.num_runs = num_runs
        self.metrics: List [PerformanceMetric] = []

        # Set up custom style settings
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#F24236',
            'tertiary': '#8F3985',
            'background': '#F8F9FA'
        }

        # Configure Seaborn style
        sns.set_theme (style="whitegrid")
        sns.set_palette ([self.colors ['primary'], self.colors ['secondary'], self.colors ['tertiary']])

    def run_benchmarks(self) -> None:
        """Run performance benchmarks for all loaders"""
        for loader in self.loaders:
            logger.info (f"Starting benchmark for {loader.__class__.__name__}")

            run_metrics = []
            for run in range (self.num_runs):
                try:
                    metric = _measure_performance (loader)
                    run_metrics.append (metric)
                    logger.info (
                        f"Run {run + 1}/{self.num_runs}: "
                        f"Time={metric.time_taken:.2f}s, "
                        f"Memory={metric.memory_used:.2f}MB, "
                        f"Throughput={metric.throughput:.0f} records/s"
                    )
                except Exception as e:
                    logger.error (f"Error in run {run + 1} for {loader.__class__.__name__}: {str (e)}")
                    continue

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

    def plot_metrics(self, save_path: Optional [str] = None) -> None:
        """Create enhanced visualizations of performance metrics"""
        if not self.metrics:
            logger.error ("No metrics to plot. Run benchmarks first.")
            return

        df = pd.DataFrame ([vars (m) for m in self.metrics])

        # Create a figure with custom layout
        fig = plt.figure (figsize=(20, 12))
        gs = GridSpec (2, 2, figure=fig)

        # Set the figure background
        fig.patch.set_facecolor (self.colors ['background'])

        # 1. Time and Memory Plot (Top Left)
        ax1 = fig.add_subplot (gs [0, 0])
        ax1.set_facecolor (self.colors ['background'])

        # Bar plot for time
        ax1.bar (df ['loader_name'], df ['time_taken'],
                 color=self.colors ['primary'], alpha=0.7)
        ax1.set_ylabel ('Time (seconds)', color=self.colors ['primary'], fontsize=12)
        ax1.tick_params (axis='y', labelcolor=self.colors ['primary'])

        # Line plot for memory
        ax2 = ax1.twinx ()
        ax2.plot (df ['loader_name'], df ['memory_used'],
                  color=self.colors ['secondary'],
                  marker='o', linewidth=2, markersize=8)
        ax2.set_ylabel ('Memory Usage (MB)', color=self.colors ['secondary'],
                        fontsize=12)
        ax2.tick_params (axis='y', labelcolor=self.colors ['secondary'])

        # Add title
        ax1.set_title ('Time and Memory Usage by Loader',
                       pad=20, fontsize=14, fontweight='bold')

        # 2. Throughput Plot (Top Right)
        ax3 = fig.add_subplot (gs [0, 1])
        ax3.set_facecolor (self.colors ['background'])

        # Create throughput bars
        throughput_bars = ax3.bar (df ['loader_name'], df ['throughput'],
                                   color=self.colors ['tertiary'], alpha=0.7)

        # Add value labels on top of bars
        for bar in throughput_bars:
            height = bar.get_height ()
            ax3.text (bar.get_x () + bar.get_width () / 2., height,
                      f'{int (height):,}',
                      ha='center', va='bottom')

        ax3.set_title ('Data Loading Throughput',
                       pad=20, fontsize=14, fontweight='bold')
        ax3.set_ylabel ('Records per Second', fontsize=12)

        # 3. CPU Usage Plot (Bottom Left)
        ax4 = fig.add_subplot (gs [1, 0])
        ax4.set_facecolor (self.colors ['background'])

        cpu_bars = ax4.bar (df ['loader_name'], df ['cpu_percent'],
                            color=self.colors ['primary'], alpha=0.7)
        ax4.set_title ('CPU Usage by Loader',
                       pad=20, fontsize=14, fontweight='bold')
        ax4.set_ylabel ('CPU Usage (%)', fontsize=12)

        # Add value labels
        for bar in cpu_bars:
            height = bar.get_height ()
            ax4.text (bar.get_x () + bar.get_width () / 2., height,
                      f'{height:.1f}%',
                      ha='center', va='bottom')

        # 4. Data Size Plot (Bottom Right)
        ax5 = fig.add_subplot (gs [1, 1])
        ax5.set_facecolor (self.colors ['background'])

        size_bars = ax5.bar (df ['loader_name'], df ['data_size'],
                             color=self.colors ['tertiary'], alpha=0.7)

        # Add value labels
        for bar in size_bars:
            height = bar.get_height ()
            ax5.text (bar.get_x () + bar.get_width () / 2., height,
                      f'{int (height):,}',
                      ha='center', va='bottom')

        ax5.set_title ('Data Size Processed',
                       pad=20, fontsize=14, fontweight='bold')
        ax5.set_ylabel ('Number of Records', fontsize=12)

        # Global figure adjustments
        plt.suptitle ('Data Loader Performance Analysis',
                      fontsize=16, fontweight='bold', y=0.95)

        # Adjust layouts and rotate labels
        for ax in [ax1, ax3, ax4, ax5]:
            ax.tick_params (axis='x', rotation=45, labelsize=10)
            # Customize grid
            ax.grid (True, linestyle='--', alpha=0.7)

        plt.tight_layout ()

        if save_path:
            plt.savefig (save_path, dpi=300, bbox_inches='tight',
                         facecolor=self.colors ['background'])
            logger.info (f"Plot saved to {save_path}")

        plt.show ()

    def generate_report(self) -> str:
        """Generate a detailed performance report"""
        if not self.metrics:
            return "No metrics available. Run benchmarks first."

        report = [
            "Performance Benchmark Report",
            "=" * 50,
            f"Generated on: {time.strftime ('%Y-%m-%d %H:%M:%S')}",
            f"Number of runs per loader: {self.num_runs}",
            "=" * 50,
            ""
        ]

        for metric in self.metrics:
            report.extend ([
                f"\nLoader: {metric.loader_name}",
                "-" * 30,
                f"Time Taken: {metric.time_taken:.2f} seconds",
                f"Memory Used: {metric.memory_used:.2f} MB",
                f"CPU Usage: {metric.cpu_percent:.1f}%",
                f"Throughput: {metric.throughput:,.0f} records/second",
                f"Data Size: {metric.data_size:,} records",
                "\nPerformance Metrics:",
                f"- Memory efficiency: {(metric.data_size / metric.memory_used):,.2f} records/MB",
                f"- Processing speed: {(1000 * metric.time_taken / metric.data_size):.2f} ms/record",
                "=" * 50
            ])

        return "\n".join (report)


# Example usage
if __name__ == "__main__":
    from Loaders.csv_loader import CSVLoader
    # from Loaders.sql_loader import SQLLoader
    # from Loaders.s3_loader import S3Loader

    # Initialize loaders
    loaders = [
        CSVLoader (file_path="C:/Users/kunya/PycharmProjects/DataVolt/data/customers-10000.csv"),
        # SQLLoader(connection_string="your_connection_string"),
        # S3Loader(bucket_name="your_bucket", file_key="your_file_key")
    ]

    # Create and run performance monitor
    monitor = PerformanceMonitor (loaders, num_runs=3)
    monitor.run_benchmarks ()

    # Generate visualizations and report
    monitor.plot_metrics (save_path="loader_performance.png")
    print (monitor.generate_report ())
