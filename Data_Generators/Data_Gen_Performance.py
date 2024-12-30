# Plot the performance of the data generators measure the time and then plot the time taken to run each data generator.

import time
import matplotlib.pyplot as plt
from Data_Generators import generate_dense_data, generate_sparse_data, tokenize_text_and_numbers, generate_other_features

# Data generators to test
data_generators = [
    generate_dense_data,
    generate_sparse_data,
    lambda: tokenize_text_and_numbers("sample text"),  # Provide a sample text argument
    generate_other_features
]

# Measure time taken for each data generator
times = []
for data_generator in data_generators:
    start_time = time.time()
    data_generator()
    end_time = time.time()
    times.append(end_time - start_time)

# Plot time taken for each data generator
plt.figure(figsize=(10, 5))
labels = ['generate_dense_data', 'generate_sparse_data', 'tokenize_text_and_numbers', 'generate_other_features']
plt.bar(labels, times)
plt.xlabel('Data Generator')
plt.ylabel('Time Taken (s)')
plt.title('Time Taken to Run Each Data Generator')
plt.show()

