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
        # Select only numeric columns
        numeric_data = data.select_dtypes(include=[float, int])
        # Compute the correlation matrix
        corr_matrix = numeric_data.corr()
        # Plot the heatmap
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
        plt.show()

    @staticmethod
    def plot_dendrogram(data):
        # Select only numeric columns
        numeric_data = data.select_dtypes(include=[float, int])
        # Drop rows with NaN values
        numeric_data = numeric_data.dropna()
        # Replace infinite values with NaN and then drop them
        numeric_data = numeric_data.replace([np.inf, -np.inf], np.nan).dropna()
        # Remove duplicate rows
        numeric_data = numeric_data.drop_duplicates()
        # Compute the linkage matrix using a different method
        linked = linkage(numeric_data, method='ward')
        # Plot the dendrogram
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
