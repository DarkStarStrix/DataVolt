# dimensionality_reduction.py

from sklearn.decomposition import PCA
from sklearn.decomposition import TruncatedSVD


def perform_pca(data, n_components=2):
    pca = PCA (n_components=n_components)
    return pca.fit_transform (data)


def perform_svd(data, n_components=2):
    svd = TruncatedSVD (n_components=n_components)
    return svd.fit_transform (data)
