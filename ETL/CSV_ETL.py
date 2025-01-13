# ETL/CSVETL.py

import pandas as pd
from sqlalchemy import create_engine
from ETL.ETL_pipeline import ETLBase

class CSVETL(ETLBase):
    def __init__(self, messages_filepath, categories_filepath, database_filepath):
        self.messages_filepath = messages_filepath
        self.categories_filepath = categories_filepath
        self.database_filepath = database_filepath

    def extract(self):
        messages = pd.read_csv(self.messages_filepath)
        categories = pd.read_csv(self.categories_filepath)
        return messages.merge(categories, on='id')

    def transform(self, data):
        categories = data['categories'].str.split(';', expand=True)
        row = categories.iloc[0]
        category_colnames = row.apply(lambda x: x.split('-')[0])
        categories.columns = category_colnames
        for column in categories:
            categories[column] = categories[column].apply(lambda x: x.split('-')[1])
            categories[column] = categories[column].astype(int)
        data = data.drop('categories', axis=1)
        data = pd.concat([data, categories], axis=1)
        data = data.drop_duplicates()
        data = data.drop('child_alone', axis=1)
        return data

    def load(self, data):
        engine = create_engine('sqlite:///' + self.database_filepath)
        data.to_sql('DisasterResponse', engine, index=False, if_exists='replace')
