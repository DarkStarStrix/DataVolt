import sqlite3
from ETL.ETL_pipeline import ETLBase

class DatabaseETL(ETLBase):
    def __init__(self, source_db_path, destination_db_path):
        self.source_db_path = source_db_path
        self.destination_db_path = destination_db_path

    def extract(self):
        conn = sqlite3.connect(self.source_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM source_table")
        data = cursor.fetchall()
        conn.close()
        return data

    def transform(self, data):
        transformed_data = []
        for row in data:
            transformed_row = (row[0], row[1].upper(), row[2] * 1.1)
            transformed_data.append(transformed_row)
        return transformed_data

    def load(self, data):
        conn = sqlite3.connect(self.destination_db_path)
        cursor = conn.cursor()
        cursor.executemany("INSERT INTO destination_table VALUES (?, ?, ?)", data)
        conn.commit()
        conn.close()


def main():
    source_db_path = 'source.db'
    destination_db_path = 'destination.db'

    etl = DatabaseETL(source_db_path, destination_db_path)
    etl.run()

if __name__ == "__main__":
    main()
