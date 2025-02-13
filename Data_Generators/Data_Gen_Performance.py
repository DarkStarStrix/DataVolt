import time
import matplotlib.pyplot as plt
from Data_Generators import generate_dense_data, generate_sparse_data, tokenize_text_and_numbers, generate_other_features

data_generators = [
    generate_dense_data,
    generate_sparse_data,
    lambda: tokenize_text_and_numbers("sample text"),
    generate_other_features
]


times = []
for data_generator in data_generators:
    start_time = time.time()
    data_generator()
    end_time = time.time()
    times.append(end_time - start_time)

plt.figure(figsize=(10, 5))
labels = ['generate_dense_data', 'generate_sparse_data', 'tokenize_text_and_numbers', 'generate_other_features']
plt.bar(labels, times)
plt.xlabel('Data Generator')
plt.ylabel('Time Taken (s)')
plt.title('Time Taken to Run Each Data Generator')
plt.show()

