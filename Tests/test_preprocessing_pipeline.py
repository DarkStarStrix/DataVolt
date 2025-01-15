# Tests/test_preprocessing_pipeline.py
import unittest
from preprocess import DataCleaner, Scaler, Encoder, PreprocessingPipeline
import pandas as pd

class TestPreprocessingPipeline(unittest.TestCase):

    def test_pipeline_process(self):
        # Sample data
        data = pd.DataFrame({
            'customer_id': [1, 2, 3],
            'age': [25, 35, 45],
            'income': [50000, 60000, 70000],
            'gender': ['M', 'F', 'M']
        })

        # Create preprocessing steps
        cleaner = DataCleaner(missing_value_strategy='fill')
        scaler = Scaler(method='minmax')
        encoder = Encoder(method='onehot')

        # Create and run a pipeline
        pipeline = PreprocessingPipeline(steps=[cleaner, scaler, encoder])
        preprocessed_data = pipeline.process(data)

        # Add assertions to verify the preprocessed data
        self.assertEqual(data.shape[0], preprocessed_data.shape[0])  # Same number of rows
        self.assertGreater(preprocessed_data.shape[1], data.shape[1])  # More columns after encoding
        self.assertFalse(preprocessed_data.isnull().values.any())  # No missing values

if __name__ == '__main__':
    unittest.main()
