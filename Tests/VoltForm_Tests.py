import unittest
from VoltForm import Main

class TestVoltForm(unittest.TestCase):
    def test_voltform(self):
        result = Main.main('C:/Users/kunya/PycharmProjects/DataVolt/VoltForm/Voltform_example.yaml')
        self.assertEqual(result, 'Success')

if __name__ == '__main__':
    unittest.main()

