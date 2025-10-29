# Example workflow for the EDA module
from pathlib import Path

from modules.eda.scripts.EDA import EDA


data_path = Path(__file__).resolve().parents[2] / "data" / "customers-10000.csv"
eda = EDA(str(data_path))

# Print the columns of the DataFrame
print("Columns in the DataFrame:", eda.data.columns)

# Print summary statistics
print(eda.summary_statistics())

# Print missing values
print(eda.missing_values())

# Plot histogram for a specific column
eda.plot_histogram('First Name')

# Plot correlation matrix
eda.plot_correlation_matrix()

# Plot scatter plot between two columns
eda.plot_scatter('First Name', 'income')

# Plot missing values heatmap
eda.plot_missing_values()
