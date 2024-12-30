import numpy as np
import pandas as pd
import random
from datetime import datetime, timedelta


def generate_other_features(num_samples=100):
    categories = ['A', 'B', 'C']
    data = {
        'categorical_feature': [random.choice (categories) for _ in range (num_samples)],
        'numerical_feature': np.random.randn (num_samples),
        'date_feature': [datetime.now () - timedelta (days=random.randint (0, 365)) for _ in range (num_samples)]
    }
    df = pd.DataFrame (data)
    return df


# Example usage
other_features_data = generate_other_features ()
print (other_features_data.head ())
