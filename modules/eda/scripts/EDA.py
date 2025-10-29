import matplotlib.pyplot as plt
import seaborn as sns


class EDA:
    def __init__(self, data):
        self.data = data

    def get_summary_statistics(self):
        return self.data.describe ()

    def get_missing_values(self):
        return self.data.isnull ().sum ()

    def plot_histogram(self, column):
        self.data [column].hist ()
        plt.title (f'Histogram of {column}')
        plt.show ()

    def plot_correlation_matrix(self):
        corr = self.data.corr ()
        sns.heatmap (corr, annot=True, cmap='coolwarm')
        plt.title ('Correlation Matrix')
        plt.show ()

    def plot_scatter(self, column1, column2):
        self.data.plot.scatter (x=column1, y=column2)
        plt.title (f'Scatter plot of {column1} vs {column2}')
        plt.show ()

    def plot_missing_values(self):
        sns.heatmap (self.data.isnull (), cbar=False, cmap='viridis')
        plt.title ('Missing Values Heatmap')
        plt.show ()
