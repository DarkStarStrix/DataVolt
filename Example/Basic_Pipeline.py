from Loaders.csv_loader import CSVLoader
from preprocess.pipeline import PreprocessingPipeline
from preprocess.scaling import Scaler
from preprocess.encoding import Encoder
from preprocess.Cleaning import DataCleaner

# Load data
loader = CSVLoader(file_path="C:/Users/kunya/PycharmProjects/DataFlux/data/customers-10000.csv")
data = loader.load_data()

# Create preprocessing steps
cleaner = DataCleaner(missing_value_strategy='fill')
scaler = Scaler(method='minmax')
encoder = Encoder(method='onehot')

# Create and run a pipeline
pipeline = PreprocessingPipeline(steps=[cleaner, scaler, encoder])
preprocessed_data = pipeline.process(data)

# Verify results
print("Original shape:", data.shape)
print("Preprocessed shape:", preprocessed_data.shape)
print("\nColumns:", preprocessed_data.columns.tolist())
