import seaborn as sns
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
import numpy as np

class DataVisualizer:
    @staticmethod
    def plot_missing_data_matrix(data):
        sns.heatmap(data.isnull(), cbar=False, cmap='viridis')
        plt.title('Missing Data Matrix')
        plt.show()

    @staticmethod
    def plot_correlation_heatmap(data):
        numeric_data = data.select_dtypes(include=[float, int])
        corr_matrix = numeric_data.corr()
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
        plt.show()

    @staticmethod
    def plot_dendrogram(data):
        numeric_data = data.select_dtypes(include=[float, int])
        numeric_data = numeric_data.dropna()
        numeric_data = numeric_data.replace([np.inf, -np.inf], np.nan).dropna()
        numeric_data = numeric_data.drop_duplicates()
        linked = linkage(numeric_data, method='ward')
        dendrogram(linked)
        plt.show()

    @staticmethod
    def plot_categorical_summary(data):
        for column in data.select_dtypes(include=['object']).columns:
            sns.countplot(y=column, data=data)
            plt.title(f'Count Plot for {column}')
            plt.show()

    @staticmethod
    def plot_numeric_summary(data):
        for column in data.select_dtypes(include=['int64', 'float64']).columns:
            sns.histplot(data[column], kde=True)
            plt.title(f'Histogram for {column}')
            plt.show()
