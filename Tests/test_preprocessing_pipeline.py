import unittest
from preprocess import DataCleaner, Scaler, Encoder, PreprocessingPipeline
import pandas as pd

class TestPreprocessingPipeline(unittest.TestCase):

    def test_pipeline_process(self):
        data = pd.DataFrame({
            'customer_id': [1, 2, 3],
            'age': [25, 35, 45],
            'income': [50000, 60000, 70000],
            'gender': ['M', 'F', 'M']
        })

        cleaner = DataCleaner(missing_value_strategy='fill')
        scaler = Scaler(method='minmax')
        encoder = Encoder(method='onehot')

        pipeline = PreprocessingPipeline(steps=[cleaner, scaler, encoder])
        preprocessed_data = pipeline.process(data)

        self.assertEqual(data.shape[0], preprocessed_data.shape[0])
        self.assertGreater(preprocessed_data.shape[1], data.shape[1])
        self.assertFalse(preprocessed_data.isnull().values.any())

if __name__ == '__main__':
    unittest.main()
