#  Write a script to test the performance of the basic pipeline and then measure the time and memory usage of the pipeline. And plot it in a graph.

import time
import psutil
import matplotlib.pyplot as plt
from Example.Basic_Pipeline import Basic_Pipeline

# Create a list to store the time and memory usage
time_list = []
memory_list = []

# Create a pipeline object
pipeline = Basic_Pipeline ()

# Run the pipeline 10 times
for i in range (10):
    # Start the timer
    start_time = time.time ()

    # Run the pipeline
    pipeline.run ()

    # End the timer
    end_time = time.time ()

    # Calculate the time taken
    time_taken = end_time - start_time

    # Get the memory usage
    memory_usage = psutil.Process ().memory_info ().rss / (1024 * 1024)  # Convert to MB

    # Append the time and memory usage to the list
    time_list.append (time_taken)
    memory_list.append (memory_usage)


# Plot the time and memory usage
def plot_graph(time_list, memory_list):
    plt.figure (figsize=(12, 6))

    plt.subplot (1, 2, 1)
    plt.plot (time_list, marker='o', label='Time (s)')
    plt.xlabel ('Run')
    plt.ylabel ('Time (s)')
    plt.title ('Time Taken for Each Run')
    plt.legend ()

    plt.subplot (1, 2, 2)
    plt.plot (memory_list, marker='o', label='Memory (MB)', color='orange')
    plt.xlabel ('Run')
    plt.ylabel ('Memory (MB)')
    plt.title ('Memory Usage for Each Run')
    plt.legend ()

    plt.tight_layout ()
    plt.show ()


plot_graph (time_list, memory_list)
