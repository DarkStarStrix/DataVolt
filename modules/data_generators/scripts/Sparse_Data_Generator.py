import pandas as pd
from scipy.sparse import random as sparse_random


def generate_sparse_data(num_samples=100, num_features=10, density=0.1):
    sparse_matrix = sparse_random (num_samples, num_features, density=density, format='csr')
    df = pd.DataFrame.sparse.from_spmatrix (sparse_matrix, columns=[f'feature_{i}' for i in range (num_features)])
    return df


sparse_data = generate_sparse_data ()
print (sparse_data.head ())
