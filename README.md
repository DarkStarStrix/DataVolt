# DataVolt: Streamline Your Data Engineering Pipelines

Currently having some issues publishing standby 

![Coverage](https://img.shields.io/badge/coverage-94%25-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![Version](https://img.shields.io/badge/version-0.0.1-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![PyPI](https://img.shields.io/badge/pypi-v0.0.1-blue)
![UV](https://img.shields.io/badge/uv-v0.0.1-blue)
[![CI](https://github.com/DarkStarStrix/DataStream/actions/workflows/Tests.yml/badge.svg)](https://github.com/DarkStarStrix/DataStream/actions/workflows/Tests.yml)

## Overview
**DataVolt** is a modular toolkit designed to automate and streamline data engineering pipelines. It provides reusable, extensible components for data loading, preprocessing, feature engineering, and model training. With DataFlux, you can save time and effort by leveraging prebuilt tools to handle repetitive and complex data engineering tasks.


Built for technical users, DataStream is ideal for:
- **Data Scientists** looking to simplify their preprocessing workflows.
- **Machine Learning Engineers** need robust pipelines for consistent data transformations.
- **Data Engineers** aiming to optimize data ingestion and transformation pipelines.

---

## Features
- **Reusable Components**: Prebuilt modules for data loading, cleaning, scaling, encoding, and more.
- **Extensibility**: Custom hooks for user-defined preprocessing and model training steps.
- **Modular Design**: Each file serves a specific purpose, ensuring flexibility and clarity.
- **Integration Ready**: Seamlessly integrate with cloud storage, SQL databases, or ML frameworks.
- **Automated Pipelines**: Chain tasks together into a functional pipeline to minimize manual coding.

---

## Installation
You can install DataStream via PyPI or UV:

```bash
pip install datavolt
```

Alternatively, using UV:

```bash
uv install datavolt
```

---

## File Structure
The toolkit is organized into modular folders:

```
DataVolt/
├── loaders/           # Modules for data ingestion
    __init__
│   ├── csv_loader.py  # Load CSV files
│   ├── sql_loader.py  # Load data from SQL databases
│   ├── s3_loader.py   # Fetch data from S3 buckets
│   └── custom_loader.py # Base class for custom loaders
├── preprocess/        # Preprocessing modules
    __init__ 
│   ├── cleaning.py    # Data cleaning utilities
│   ├── encoding.py    # Encoding categorical variables
│   ├── scaling.py     # Data scaling and normalization
│   ├── feature_engineering.py # Feature engineering tools
│   └── pipeline.py    # Orchestrates preprocessing steps
├── ext/               # Extensions and utilities
│   ├── logger.py      # Logging utilities
│   ├── custom_step.py # Hooks for custom pipeline steps
└── README.md          # Project documentation
```

---

Initial commit: Add DataStream project with modular toolkit for data engineering pipelines## Quick Start Guide

### Step 1: Load Your Data
Choose a loader module based on your data source:

```python
from datavolt.loaders.csv_loader import CSVLoader

loader = CSVLoader(file_path="data.csv")
data = loader.load()
```

### Step 2: Preprocess Your Data
Use the preprocessing modules to clean and transform your data:

```python
from datavolt.preprocess.pipeline import PreprocessingPipeline
from datavolt.preprocess.scaling import StandardScaler
from datavolt.preprocess.encoding import OneHotEncoder

pipeline = PreprocessingPipeline([
    StandardScaler(),
    OneHotEncoder()
])
preprocessed_data = pipeline.run(data)
```

### Step 3: Train a Model
Pass the preprocessed data into the model training module:

```python
from datavolt.model.trainer import ModelTrainer

trainer = ModelTrainer(model="random_forest", parameters={"n_estimators": 100})
trained_model = trainer.train(preprocessed_data, labels)
```

### Step 4: Evaluate and Export
Evaluate the model and save it for deployment:

```python
from datavolt.model.evaluator import Evaluator
from datavolt.model.model_export import ModelExporter

evaluator = Evaluator()
metrics = evaluator.evaluate(trained_model, test_data, test_labels)
print(metrics)

exporter = ModelExporter()
exporter.save(trained_model, "models/random_forest.pkl")
```

---

## Why Use DataVolt?
### In the Data Engineering Ecosystem:
DataVolt addresses key challenges in the modern data engineering landscape:
1. **Reusability**: Standardize and modularize workflows to prevent redundant code.
2. **Consistency**: Ensures uniform data transformations across projects.
3. **Efficiency**: Reduces the time spent on routine data preprocessing and model setup tasks.
4. **Scalability**: Easily adapted to different data sources and project scales.

### Example Use Case:
In a machine learning workflow, DataStream can:
- Load large datasets from cloud storage.
- Clean and preprocess them for feature selection.
- Automate model training and hyperparameter tuning.
- Track experiment metrics and export production-ready models.

---

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch.
3. Commit your changes and submit a pull request.

---

## License
DataVolt is licensed under the MIT License. See `LICENSE` for details.

---

## Support
For questions, issues, or feature requests, please open a GitHub issue or contact me at [allanw.mk@gmail.com]).

---

### Happy Streamlining with DataVolt
