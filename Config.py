# Config.py

# Data settings
DATA_PATH = "data/"
DATA_FILE = "data.csv"
LABELS_FILE = "labels.csv"

# Preprocessing settings
MISSING_VALUE_STRATEGY = 'fill'
SCALING_METHOD = 'minmax'
ENCODING_METHOD = 'onehot'

# Model settings
MODEL_SAVE_PATH = "models/random_forest.pkl"
TEST_SIZE = 0.2
RANDOM_STATE = 42

# Training settings
BATCH_SIZE = 32
EPOCHS = 10
LEARNING_RATE = 0.001

# Augmentation settings
AUGMENT = True
AUGMENT_FLIP = True
AUGMENT_ROTATE = True
AUGMENT_SHIFT = True

# Evaluation settings
METRICS = ['accuracy', 'precision', 'recall', 'f1']

# Deployment settings
