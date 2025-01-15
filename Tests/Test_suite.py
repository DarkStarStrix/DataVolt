import unittest
import os

# Ensure the current working directory is set to the project root
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Discover and run all tests in the 'Tests' directory
if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir='.', pattern='test_*.py')

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
