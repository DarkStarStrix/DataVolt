# Tests/test_csv_loader.py
import unittest
from Loaders.csv_loader import CSVLoader

class TestCSVLoader(unittest.TestCase):

    def test_load_data(self):
        file_path = "C:/Users/kunya/PycharmProjects/DataVolt/data/customers-100.csv"
        loader = CSVLoader(file_path)
        data = loader.load_data()

        # Add assertions to verify the loaded data
        self.assertIsNotNone(data)
        self.assertFalse(data.empty)
        self.assertIn('customer_id', data.columns)

if __name__ == '__main__':
    unittest.main()
