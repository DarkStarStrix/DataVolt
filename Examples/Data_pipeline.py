import os
import pandas as pd
from Loaders.csv_loader import CSVLoader
from preprocess.Cleaning import DataCleaner
from tabulate import tabulate

# Define file paths
input_file_path = 'C:/Users/kunya/PycharmProjects/DataStream/data/customers-100.csv'
output_dir = 'C:/Users/kunya/PycharmProjects/DataStream/data/processed_data'
output_file_path = os.path.join (output_dir, 'processed_customers-100.csv')

# Create the output directory if it doesn't exist
os.makedirs (output_dir, exist_ok=True)


# Function to process a single file
def process_file(input_file, output_file):
    # Load data
    loader = CSVLoader (file_path=input_file)
    data = loader.load_data ()

    # Print the original dataset
    print ("Original Dataset:")
    print (data)

    # Create preprocessing steps
    cleaner = DataCleaner (missing_value_strategy='fill')

    # Clean the data
    cleaned_data = cleaner.transform (data)

    # Exclude columns with all zero values
    cleaned_data = cleaned_data.loc [:, (cleaned_data != 0).any (axis=0)]

    # Generate summary statistics for all columns
    summary_stats = cleaned_data.describe (include='all').transpose ()

    # Save summary statistics to a text file
    with open (os.path.join (output_dir, 'summary_statistics.txt'), 'w') as f:
        f.write ("Summary Statistics:\n")
        f.write (tabulate (summary_stats, headers='keys', tablefmt='grid'))

    # Print the processed data to the console
    print ("Cleaned Data:")
    print (cleaned_data)

    # Save the cleaned data
    cleaned_data.to_csv (output_file, index=False)


# Process the file
process_file (input_file_path, output_file_path)

print ("Data processing complete. Processed file and summary statistics are saved in the 'processed_data' folder.")
