import pandas as pd
import sqlalchemy


class SQLLoader:
    def __init__(self, connection_string, query):
        self.connection_string = connection_string
        self.query = query

    def load_data(self):
        engine = sqlalchemy.create_engine (self.connection_string)
        return pd.read_sql_query (self.query, engine)
