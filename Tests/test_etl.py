# Tests/test_etl.py
import unittest
from ETL.ETL_pipeline import ETLBase

class TestETLProcessor(unittest.TestCase):

    def test_extract(self):
        processor = ETLBase()
        data = processor.extract()
        self.assertIsNotNone(data)
        self.assertFalse(data.empty)

    def test_transform(self):
        processor = ETLBase()
        raw_data = processor.extract()
        transformed_data = processor.transform(raw_data)
        self.assertIsNotNone(transformed_data)
        self.assertFalse(transformed_data.empty)

    def test_load(self):
        processor = ETLBase()
        raw_data = processor.extract()
        transformed_data = processor.transform(raw_data)
        result = processor.load(transformed_data)
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()