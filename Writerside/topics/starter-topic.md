# Quick Start Guide

### Step 1: Load Your Data
Choose a loader module based on your data source:

```python
from datastream.loaders.csv_loader import CSVLoader

loader = CSVLoader(file_path="data.csv")
data = loader.load()
```

### Step 2: Preprocess Your Data
Use the preprocessing modules to clean and transform your data:

```python
from dataflux.preprocess.pipeline import PreprocessingPipeline
from dataflux.preprocess.scaling import Scaler
from dataflux.preprocess.encoding import Encoder
from dataflux.preprocess.cleaning import DataCleaner

pipeline = PreprocessingPipeline([
    DataCleaner(missing_value_strategy='fill'),
    Scaler(method='minmax'),
    Encoder(method='onehot')
])
preprocessed_data = pipeline.process(data)
```

### Step 3: Train a Model
Pass the preprocessed data into the model training module:

```python
from datastream.model.trainer import ModelTrainer

trainer = ModelTrainer(model="random_forest", parameters={"n_estimators": 100})
trained_model = trainer.train(preprocessed_data, labels)
```

### Step 4: Evaluate and Export
Evaluate the model and save it for deployment:

```python
from dataflux.model.evaluator import Evaluator
from dataflux.model.model_export import ModelExporter

evaluator = Evaluator()
metrics = evaluator.evaluate(trained_model, test_data, test_labels)
print(metrics)

exporter = ModelExporter()
exporter.save(trained_model, "models/random_forest.pkl")
```
```

This will guide users on how to install and use your `DataFlux` library.
