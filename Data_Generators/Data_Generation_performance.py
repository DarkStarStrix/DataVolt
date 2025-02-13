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


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Data class to store performance metrics"""
    loader_name: str
    time_taken: float
    memory_used: float
    cpu_percent: float

def _measure_performance(loader) -> PerformanceMetric:
    """Measure the performance of a data loader."""
    start_time = time.time()
    process = psutil.Process()
    start_memory = process.memory_info().rss
    start_cpu = process.cpu_percent(interval=None)

    loader.generate_data (10000)

    end_time = time.time()
    end_memory = process.memory_info().rss
    end_cpu = process.cpu_percent(interval=None)

    time_taken = end_time - start_time
    memory_used = (end_memory - start_memory) / (1024 * 1024)  # Convert to MB
    cpu_percent = end_cpu - start_cpu

    return PerformanceMetric(
        loader_name=loader.__class__.__name__,
        time_taken=time_taken,
        memory_used=memory_used,
        cpu_percent=cpu_percent
    )

class PerformanceMonitor:
    """Monitor and visualize loader performance"""

    def __init__(self, loaders: List[Any], num_runs: int = 3):
        self.loaders = loaders
        self.num_runs = num_runs
        self.metrics: List[PerformanceMetric] = []

        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#F24236',
            'tertiary': '#8F3985',
            'background': '#F8F9FA'
        }

        sns.set_theme(style="whitegrid")
        sns.set_palette([self.colors['primary'], self.colors['secondary'], self.colors['tertiary']])

    def run_benchmarks(self) -> None:
        """Run performance benchmarks for all loaders"""
        for loader in self.loaders:
            logger.info(f"Starting benchmark for {loader.__class__.__name__}")

            run_metrics = []
            for run in range(self.num_runs):
                try:
                    metric = _measure_performance(loader)
                    run_metrics.append(metric)
                    logger.info(
                        f"Run {run + 1}/{self.num_runs}: "
                        f"Time={metric.time_taken:.2f}s, "
                        f"Memory={metric.memory_used:.2f}MB, "
                        f"CPU={metric.cpu_percent:.1f}%"
                    )
                except Exception as e:
                    logger.error(f"Error in run {run + 1} for {loader.__class__.__name__}: {str(e)}")
                    continue

            if run_metrics:
                avg_metric = PerformanceMetric(
                    loader_name=loader.__class__.__name__,
                    time_taken=np.mean([m.time_taken for m in run_metrics]),
                    memory_used=np.mean([m.memory_used for m in run_metrics]),
                    cpu_percent=np.mean([m.cpu_percent for m in run_metrics])
                )
                self.metrics.append(avg_metric)

    def plot_metrics(self, save_path: Optional[str] = None) -> None:
        """Create enhanced visualizations of performance metrics"""
        if not self.metrics:
            logger.error("No metrics to plot. Run benchmarks first.")
            return

        df = pd.DataFrame([vars(m) for m in self.metrics])

        fig = plt.figure(figsize=(20, 12))
        gs = GridSpec(2, 2, figure=fig)


        fig.patch.set_facecolor(self.colors['background'])

        ax1 = fig.add_subplot(gs[0, 0])
        ax1.set_facecolor(self.colors['background'])

        ax1.bar(df['loader_name'], df['time_taken'],
                color=self.colors['primary'], alpha=0.7)
        ax1.set_ylabel('Time (seconds)', color=self.colors['primary'], fontsize=12)
        ax1.tick_params(axis='y', labelcolor=self.colors['primary'])

        ax2 = ax1.twinx()
        ax2.plot(df['loader_name'], df['memory_used'],
                 color=self.colors['secondary'],
                 marker='o', linewidth=2, markersize=8)
        ax2.set_ylabel('Memory Usage (MB)', color=self.colors['secondary'],
                       fontsize=12)
        ax2.tick_params(axis='y', labelcolor=self.colors['secondary'])

        ax1.set_title('Time and Memory Usage by Data generator',
                      pad=20, fontsize=14, fontweight='bold')

        ax3 = fig.add_subplot(gs[0, 1])
        ax3.set_facecolor(self.colors['background'])

        cpu_bars = ax3.bar(df['loader_name'], df['cpu_percent'],
                           color=self.colors['primary'], alpha=0.7)
        ax3.set_title('CPU Usage by Data generator',
                      pad=20, fontsize=14, fontweight='bold')
        ax3.set_ylabel('CPU Usage (%)', fontsize=12)

        for bar in cpu_bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width() / 2., height,
                     f'{height:.1f}%',
                     ha='center', va='bottom')

        plt.suptitle('Data Generation Performance Analysis',
                     fontsize=16, fontweight='bold', y=0.95)

        for ax in [ax1, ax3]:
            ax.tick_params(axis='x', rotation=45, labelsize=10)
            ax.grid(True, linestyle='--', alpha=0.7)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight',
                        facecolor=self.colors['background'])
            logger.info(f"Plot saved to {save_path}")

        plt.show()

    def generate_report(self) -> str:
        """Generate a detailed performance report"""
        if not self.metrics:
            return "No metrics available. Run benchmarks first."

        report = [
            "Performance Benchmark Report",
            "=" * 50,
            f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Number of runs per loader: {self.num_runs}",
            "=" * 50,
            ""
        ]

        for metric in self.metrics:
            report.extend([
                f"\nLoader: {metric.loader_name}",
                "-" * 30,
                f"Time Taken: {metric.time_taken:.2f} seconds",
                f"Memory Used: {metric.memory_used:.2f} MB",
                f"CPU Usage: {metric.cpu_percent:.1f}%",
                "=" * 50
            ])

        return "\n".join(report)


if __name__ == "__main__":
    from Data_Generators.data_generator import DataGenerator

    data_gen = DataGenerator()

    monitor = PerformanceMonitor([data_gen], num_runs=3)
    monitor.run_benchmarks()

    monitor.plot_metrics(save_path="data_gen_performance.png")
    print(monitor.generate_report())
