import time
import psutil
import matplotlib.pyplot as plt
from Loaders.csv_loader import CSVLoader
from Loaders.sql_loader import SQLLoader
from Loaders.s3_loader import S3Loader

# List of loaders to test
loaders = [
    CSVLoader (file_path="C:/Users/kunya/PycharmProjects/DataStream/data/customers-10000.csv"),
    SQLLoader (connection_string="your_connection_string", query="SELECT * FROM your_table"),
    S3Loader (bucket_name="your_bucket", file_key="your_file_key")
]

# Create lists to store the time and memory usage
time_list = []
memory_list = []

# Run each loader and measure performance
for loader in loaders:
    # Start the timer
    start_time = time.time ()

    # Load the data
    data = loader.load_data ()

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
    plt.bar (['CSVLoader', 'SQLLoader', 'S3Loader'], time_list, color='blue')
    plt.xlabel ('Loader')
    plt.ylabel ('Time (s)')
    plt.title ('Time Taken for Each Loader')

    plt.subplot (1, 2, 2)
    plt.bar (['CSVLoader', 'SQLLoader', 'S3Loader'], memory_list, color='orange')
    plt.xlabel ('Loader')
    plt.ylabel ('Memory (MB)')
    plt.title ('Memory Usage for Each Loader')

    plt.tight_layout ()
    plt.show ()


plot_graph (time_list, memory_list)
