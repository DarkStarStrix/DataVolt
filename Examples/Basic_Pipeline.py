from Loaders.csv_loader import CSVLoader
from preprocess.Cleaning import DataCleaner
from preprocess.scaling import Scaler
from preprocess.encoding import Encoder
from preprocess.pipeline import PreprocessingPipeline

# Initialize components
loader = CSVLoader("C:/Users/kunya/PycharmProjects/DataStream/data/customers-10000.csv")
cleaner = DataCleaner(missing_value_strategy='fill')
scaler = Scaler(method='minmax')
encoder = Encoder(method='onehot')

# Create a pipeline
pipeline = PreprocessingPipeline([
    cleaner,
    scaler,
    encoder
])

# Process data
data = loader.load_data()
processed_data = pipeline.process(data)

print(processed_data.head())


# Example/Basic_Pipeline.py

class Basic_Pipeline:
    @staticmethod
    def run():
        # Your pipeline code here
        print ("Running the pipeline")
