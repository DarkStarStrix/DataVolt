import time
import psutil
import matplotlib.pyplot as plt
from Examples.Basic_Pipeline import Basic_Pipeline
from EDA.dimensionality import perform_pca, perform_svd
import numpy as np

# Create a list to store the time and memory usage
time_list = []
memory_list = []

# Create a pipeline object
pipeline = Basic_Pipeline ()

# Number of elements to process
num_elements = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

# Run the pipeline for different number of elements
for elements in num_elements:
    run_times = []
    for _ in range (10):  # Run each configuration 10 times
        start_time = time.time ()
        preprocessed_data = pipeline.run ()  # Assuming the pipeline can take the number of elements as an argument

        # Check if preprocessed_data is None
        if preprocessed_data is None:
            continue

        # Ensure preprocessed_data is a 2D array
        if np.isscalar (preprocessed_data):
            preprocessed_data = np.array ([[preprocessed_data]])
        elif preprocessed_data.ndim == 1:
            preprocessed_data = preprocessed_data.reshape (-1, 1)

        pca_data = perform_pca (preprocessed_data)
        svd_data = perform_svd (preprocessed_data)
        end_time = time.time ()
        run_times.append (end_time - start_time)

    # Calculate the average time taken
    avg_time_taken = sum (run_times) / len (run_times) if run_times else 0
    time_list.append (avg_time_taken)

    # Get the memory usage
    memory_usage = psutil.Process ().memory_info ().rss / (1024 * 1024)  # Convert to MB
    memory_list.append (memory_usage)


# Plot the number of elements against the average time taken
def plot_graph(num_elements, time_list, memory_list):
    plt.figure (figsize=(12, 6))

    plt.subplot (1, 2, 1)
    plt.bar (num_elements, time_list, label='Average Time (s)')
    plt.xlabel ('Number of Elements')
    plt.ylabel ('Average Time (s)')
    plt.title ('Average Time Taken for Each Number of Elements')
    plt.legend ()

    plt.subplot (1, 2, 2)
    plt.bar (num_elements, memory_list, label='Memory (MB)', color='orange')
    plt.xlabel ('Number of Elements')
    plt.ylabel ('Memory (MB)')
    plt.title ('Memory Usage for Each Number of Elements')
    plt.legend ()

    plt.tight_layout ()
    plt.show ()


plot_graph (num_elements, time_list, memory_list)
