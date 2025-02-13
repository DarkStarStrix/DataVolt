import numpy as np
import pandas as pd


def generate_dense_data(num_samples=100, num_features=10):
    data = np.random.rand (num_samples, num_features)
    df = pd.DataFrame (data, columns=[f'feature_{i}' for i in range (num_features)])
    return df


dense_data = generate_dense_data ()
print (dense_data.head ())
