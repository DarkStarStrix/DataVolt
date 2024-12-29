import unittest
import pandas as pd
from preprocess.encoding import Encoder


class TestPipeline(unittest.TestCase):

    def test_encoding_onehot_with_categorical_columns(self):
        data = pd.DataFrame({
            'color': ['red', 'blue', 'green'],
            'size': ['S', 'M', 'L']
        })
        encoder = Encoder(method='onehot')
        result = encoder.transform(data)
        expected_columns = ['color_blue', 'color_green', 'color_red', 'size_L', 'size_M', 'size_S']
        self.assertTrue(all(col in result.columns for col in expected_columns))
        self.assertEqual(result.shape, (3, 6))

    def test_encoding_onehot_with_no_categorical_columns(self):
        data = pd.DataFrame({
            'height': [150, 160, 170],
            'weight': [50, 60, 70]
        })
        encoder = Encoder(method='onehot')
        result = encoder.transform(data)
        self.assertTrue(result.equals(data))

    def test_encoding_with_unsupported_method(self):
        data = pd.DataFrame({
            'color': ['red', 'blue', 'green']
        })
        encoder = Encoder(method='unsupported')
        with self.assertRaises(ValueError):
            encoder.transform(data)

    def test_encoding_with_empty_dataframe(self):
        data = pd.DataFrame()
        encoder = Encoder(method='onehot')
        result = encoder.transform(data)
        self.assertTrue(result.empty)


if __name__ == '__main__':
    unittest.main()
