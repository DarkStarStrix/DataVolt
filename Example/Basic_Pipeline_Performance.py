#  Write a script to test the performance of the basic pipeline and then measure the time and memory usage of the pipeline. And plot it in a graph.

import time
import psutil
import matplotlib.pyplot as plt
from Example.Basic_Pipeline import Basic_Pipeline

# Create lists to store the time and memory usage
time_list = []
memory_list = []

# Create a pipeline object
pipeline = Basic_Pipeline ()

# Number of elements to process
num_elements = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

# Run the pipeline for different number of elements
for elements in num_elements:
    run_times = []
    memory_runs = []

    for _ in range (10):  # Run each configuration 10 times
        # Clear any garbage before measuring
        psutil.Process ().memory_info ()  # Initial call to stabilize

        start_time = time.time ()
        pipeline.run ()  # Assuming the pipeline can take the number of elements
        end_time = time.time ()

        run_times.append (end_time - start_time)
        memory_usage = psutil.Process ().memory_info ().rss / (1024 * 1024)  # Convert to MB
        memory_runs.append (memory_usage)

    # Calculate averages
    avg_time_taken = sum (run_times) / len (run_times)
    avg_memory_usage = sum (memory_runs) / len (memory_runs)

    time_list.append (avg_time_taken)
    memory_list.append (avg_memory_usage)


def plot_graph(num_elements, time_list, memory_list):
    plt.figure (figsize=(12, 6))

    # Time plot
    plt.subplot (1, 2, 1)
    plt.bar (num_elements, time_list, color='blue', width=8)
    plt.xlabel ('Number of Elements')
    plt.ylabel ('Average Time (s)')
    plt.title ('Average Time Taken for Each Number of Elements')
    # Ensure y-axis starts at 0
    plt.ylim (bottom=0)

    # Memory plot
    plt.subplot (1, 2, 2)
    plt.bar (num_elements, memory_list, color='orange', width=8)
    plt.xlabel ('Number of Elements')
    plt.ylabel ('Memory (MB)')
    plt.title ('Memory Usage for Each Number of Elements')
    # Ensure y-axis starts at 0
    plt.ylim (bottom=0)

    plt.tight_layout ()
    plt.show ()


plot_graph (num_elements, time_list, memory_list)
