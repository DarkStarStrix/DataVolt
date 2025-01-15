# ETL/CSVETL.py

import pandas as pd
from sqlalchemy import create_engine
from ETL.ETL_pipeline import ETLBase

class CSVETL(ETLBase):
    def __init__(self, file_path, database_filepath, processed_filepath):
        self.file_path = file_path
        self.database_filepath = database_filepath
        self.processed_filepath = processed_filepath

    def extract(self):
        # Extract data from the CSV file
        data = pd.read_csv(self.file_path)
        return data

    def transform(self, data):
        # Example transformation: fill missing values with 0
        transformed_data = data.fillna(0)
        return transformed_data

    def load(self, data):
        # Load data into a SQLite database
        engine = create_engine('sqlite:///' + self.database_filepath)
        data.to_sql('Financials', engine, index=False, if_exists='replace')

        # Save the processed data to a CSV file
        data.to_csv(self.processed_filepath, index=False)
