import pandas as pd
import numpy as np

class DataGenerator:
    @staticmethod
    def generate_data(num_samples):
        # Generate random data
        data = pd.DataFrame({
            'id': np.arange(num_samples),
            'value': np.random.rand(num_samples)
        })
        return data

    @staticmethod
    def generate_data_with_schema(schema, num_samples):
        # Generate data based on schema
        data = {}
        for column, dtype in schema.items():
            if dtype == 'str':
                data[column] = ['sample'] * num_samples
            elif dtype == 'int':
                data[column] = np.random.randint(0, 100, num_samples)
            elif dtype == 'float':
                data[column] = np.random.rand(num_samples)
        return pd.DataFrame(data)
