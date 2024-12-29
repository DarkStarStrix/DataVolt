from sklearn.preprocessing import MinMaxScaler, StandardScaler
import pandas as pd


class Scaler:
    def __init__(self, method='minmax'):
        self.method = method
        self.scalers = {}

    def transform(self, data):
        result = data.copy ()

        # Select only numeric columns
        numeric_columns = data.select_dtypes (include=['int64', 'float64']).columns

        if len (numeric_columns) == 0:
            return result

        for column in numeric_columns:
            if column not in self.scalers:
                if self.method == 'minmax':
                    self.scalers [column] = MinMaxScaler ()
                elif self.method == 'standard':
                    self.scalers [column] = StandardScaler ()

                # Reshape for scaling
                values = result [column].values.reshape (-1, 1)
                self.scalers [column].fit (values)

            # Transform the column
            values = result [column].values.reshape (-1, 1)
            result [column] = self.scalers [column].transform (values)

        return result
