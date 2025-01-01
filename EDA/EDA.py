# eda.py

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class EDA:
    def __init__(self, file_path):
        self.data = pd.read_csv (file_path)

    def summary_statistics(self):
        return self.data.describe ()

    def missing_values(self):
        return self.data.isnull ().sum ()

    def plot_histogram(self, column):
        plt.figure (figsize=(10, 6))
        sns.histplot (self.data [column], kde=True)
        plt.title (f'Histogram of {column}')
        plt.show ()

    def plot_correlation_matrix(self):
        plt.figure (figsize=(12, 8))
        sns.heatmap (self.data.corr (), annot=True, cmap='coolwarm')
        plt.title ('Correlation Matrix')
        plt.show ()

    def plot_scatter(self, column1, column2):
        plt.figure (figsize=(10, 6))
        sns.scatterplot (x=self.data [column1], y=self.data [column2])
        plt.title (f'Scatter Plot of {column1} vs {column2}')
        plt.show ()

    def plot_missing_values(self):
        plt.figure (figsize=(12, 6))
        sns.heatmap (self.data.isnull (), cbar=False, cmap='viridis')
        plt.title ('Missing Values Heatmap')
        plt.show ()
