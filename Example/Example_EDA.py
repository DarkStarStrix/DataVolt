# EDA/EDA.py

from EDA.EDA import EDA

# Initialize the EDA object with the path to your CSV file
eda = EDA('C:/Users/kunya/PycharmProjects/DataStream/data/customers-10000.csv')

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
