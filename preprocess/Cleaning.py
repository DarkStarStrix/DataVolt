# preprocess/cleaning.py
import pandas as pd
import numpy as np


class DataCleaner:
    def __init__(self, missing_value_strategy='fill'):
        self.strategy = missing_value_strategy
        self.fill_values = {}

    def transform(self, data):
        result = data.copy ()

        # Handle missing values
        if self.strategy == 'fill':
            for column in result.columns:
                if result [column].dtype in ['int64', 'float64']:
                    self.fill_values [column] = result [column].mean ()
                else:
                    self.fill_values [column] = result [column].mode () [0]
                result [column] = result [column].fillna (self.fill_values [column])
        elif self.strategy == 'drop':
            result = result.dropna ()

        # Remove duplicates
        result = result.drop_duplicates ()

        # Handle special characters in string columns
        string_columns = result.select_dtypes (include=['object']).columns
        for column in string_columns:
            result [column] = result [column].str.strip ()
            # Remove special characters if needed
            # result[column] = result[column].str.replace('[^\w\s]', '')

        return result
