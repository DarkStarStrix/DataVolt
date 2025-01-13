# Quick Start Guide

### Step 1: Load Your Data
Choose a loader module based on your data source:

```python
from Loaders.csv_loader import CSVLoader

loader = CSVLoader(file_path="data.csv")
data = loader.load()
```

### Step 2: Preprocess Your Data
Use the preprocessing modules to clean and transform your data:

```python
from preprocess.pipeline import PreprocessingPipeline
from preprocess.scaling import Scaler
from preprocess.encoding import Encoder
from preprocess.Cleaning import DataCleaner

pipeline = PreprocessingPipeline([
    DataCleaner(missing_value_strategy='fill'),
    Scaler(method='minmax'),
    Encoder(method='onehot')
])
preprocessed_data = pipeline.process(data)
```

This will guide users on how to install and use your `DataFlux` library.
