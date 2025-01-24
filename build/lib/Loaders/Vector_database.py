# Loaders/Vector_database.py
import sqlalchemy
from sqlalchemy import Table, Column, Integer, Float, MetaData

class VectorDatabase:
    def __init__(self, connection_string, table_name):
        self.connection_string = connection_string
        self.table_name = table_name
        self.engine = sqlalchemy.create_engine(self.connection_string)
        self.metadata = MetaData(self.engine)
        self.table = Table(self.table_name, self.metadata,
                           Column('id', Integer, primary_key=True),
                           Column('vector', Float, nullable=False))

    def create_table(self):
        self.metadata.create_all(self.engine)

    def insert_vector(self, vector):
        with self.engine.connect() as connection:
            insert_stmt = self.table.insert().values(vector=vector)
            connection.execute(insert_stmt)

    def query_vectors(self):
        with self.engine.connect() as connection:
            select_stmt = self.table.select()
            result = connection.execute(select_stmt)
            return [row['vector'] for row in result]

    def close(self):
        self.engine.dispose()
