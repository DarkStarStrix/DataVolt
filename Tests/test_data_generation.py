import unittest
from Data_Generators.data_generator import DataGenerator

class TestDataGenerator(unittest.TestCase):

    def test_generate_data(self):
        generator = DataGenerator()
        data = generator.generate_data(num_samples=100)
        self.assertIsNotNone(data)
        self.assertEqual(len(data), 100)

    def test_generate_data_with_schema(self):
        generator = DataGenerator()
        schema = {'name': 'str', 'age': 'int', 'income': 'float'}
        data = generator.generate_data_with_schema(schema, num_samples=100)
        self.assertIsNotNone(data)
        self.assertEqual(len(data), 100)
        self.assertIn('name', data.columns)
        self.assertIn('age', data.columns)
        self.assertIn('income', data.columns)

if __name__ == '__main__':
    unittest.main()
