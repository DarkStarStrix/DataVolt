import time
import plotly.express as px
from Dense_Data_Generator import generate_dense_data
from Sparse_Data_Generator import generate_sparse_data
from General_Data_Features import generate_other_features
from Tokenizing_Text_Data import tokenize_text_and_numbers


# Measure execution time for each function
def measure_time(func, *args, **kwargs):
    start_time = time.time ()
    func (*args, **kwargs)
    end_time = time.time ()
    return end_time - start_time


# Measure times
times = {
    'Dense Data': measure_time (generate_dense_data, num_samples=1000, num_features=50),
    'Sparse Data': measure_time (generate_sparse_data, num_samples=1000, num_features=50, density=0.1),
    'Other Features': measure_time (generate_other_features, num_samples=1000),
    'Tokenizing Text': measure_time (tokenize_text_and_numbers, "This is an example sentence with numbers 123 and 456.")
}

# Print times
for key, value in times.items ():
    print (f"{key}: {value:.4f} seconds")


# Plot the execution times using Plotly
def plot_times(times):
    labels = list (times.keys ())
    values = list (times.values ())

    fig = px.bar (x=labels, y=values, labels={'x': 'Scripts', 'y': 'Execution Time (seconds)'},
                  title='Performance Metrics of Data Generation Scripts')
    fig.show ()


# Plot the times
plot_times (times)
