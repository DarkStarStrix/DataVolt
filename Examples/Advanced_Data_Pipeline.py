import os
from Loaders.csv_loader import CSVLoader
from preprocess import DataCleaner, DataVisualizer, Encoder
import time

# Define file paths
input_file_path = 'C:/Users/kunya/PycharmProjects/DataVolt/data/housing.csv'
output_dir = 'C:/Users/kunya/PycharmProjects/DataVolt/data/processed_data'
output_file_path = os.path.join(output_dir, 'processed_housing.csv')

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Load data
loader = CSVLoader(file_path=input_file_path)
data = loader.load_data()

# Clean data
cleaner = DataCleaner(missing_value_strategy='mean')
cleaned_data = cleaner.transform(data)

# Encode categorical data
encoder = Encoder()
encoded_data = encoder.transform(cleaned_data)

# Initialize visualizer
visualizer = DataVisualizer()

# Visualize data based on type
visualizer.plot_numeric_summary(cleaned_data)
visualizer.plot_categorical_summary(data)

# Visualize correlation heatmap
visualizer.plot_correlation_heatmap(encoded_data)


# Simple numeric summaries
print("Numeric Summaries:")
print(encoded_data.describe())

# Save the cleaned data
encoded_data.to_csv(output_file_path, index=False)

# print time taken to process data
print("Time taken to process data: ", time.process_time())

print("Data processing complete. Processed file is saved in the 'processed_data' folder.")
