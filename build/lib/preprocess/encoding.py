import pandas as pd
from sklearn.preprocessing import OneHotEncoder


class Encoder:
    def __init__(self, method='onehot'):
        self.method = method
        self.encoders = {}  # Store an encoder for each categorical column

    def transform(self, data):
        # Make a copy to avoid modifying original data
        result = data.copy()

        # Get categorical columns
        categorical_columns = data.select_dtypes(include=['object']).columns

        if len(categorical_columns) == 0:
            return result

        # Process each categorical column
        for column in categorical_columns:
            print(f"Processing column: {column}")

            # Check if we need to fit a new encoder
            if column not in self.encoders:
                self.encoders[column] = OneHotEncoder(handle_unknown='ignore')
                # Fit the encoder and get feature names
                self.encoders[column].fit(data[[column]])

            # Transform the data
            encoded_data = self.encoders[column].transform(data[[column]]).toarray()
            print(f"Encoded data shape for column {column}: {encoded_data.shape}")

            # Get feature names
            feature_names = self.encoders[column].get_feature_names_out([column])
            print(f"Feature names for column {column}: {feature_names}")

            # Create DataFrame with the correct shape
            encoded_df = pd.DataFrame(
                encoded_data,
                columns=feature_names,
                index=data.index
            )
            print(f"Encoded DataFrame shape for column {column}: {encoded_df.shape}")

            # Drop the original column and join encoded columns
            result = result.drop(columns=[column])
            result = pd.concat([result, encoded_df], axis=1)
            print(f"Resulting DataFrame shape after encoding column {column}: {result.shape}")

        return result

    def fit_transform(self, data):
        return self.transform(data)
