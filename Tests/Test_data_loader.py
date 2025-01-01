import sys
import os
import unittest
from Loaders.csv_loader import CSVLoader  # Adjust the path as necessary
from preprocess.pipeline import PreprocessingPipeline
from preprocess.scaling import Scaler
from preprocess.encoding import Encoder
from preprocess.Cleaning import DataCleaner  # Ensure the correct case for the module name
import concurrent.futures

sys.path.insert (0, os.path.abspath (os.path.join (os.path.dirname (__file__), '..')))


class TestIntegration (unittest.TestCase):

    def test_pipeline_integration(self):
        file_paths = [
            "C:/Users/kunya/PycharmProjects/DataFlux/data/customers-100.csv",
            "C:/Users/kunya/PycharmProjects/DataFlux/data/customers-1000.csv",
            "C:/Users/kunya/PycharmProjects/DataFlux/data/customers-10000.csv"
        ]

        def process_file(file_path):
            loader = CSVLoader (file_path=file_path)
            data = loader.load_data ()

            # Create preprocessing steps
            cleaner = DataCleaner (missing_value_strategy='fill')
            scaler = Scaler (method='minmax')
            encoder = Encoder (method='onehot')

            # Create and run a pipeline
            pipeline = PreprocessingPipeline (steps=[cleaner, scaler, encoder])
            preprocessed_data = pipeline.process (data)

            # Verify results
            self.assertEqual (data.shape [0], preprocessed_data.shape [0])  # Same number of rows
            self.assertGreater (preprocessed_data.shape [1], data.shape [1])  # More columns after encoding
            self.assertFalse (preprocessed_data.isnull ().values.any ())  # No missing values

        with concurrent.futures.ThreadPoolExecutor () as executor:
            executor.map (process_file, file_paths)


if __name__ == '__main__':
    unittest.main ()
