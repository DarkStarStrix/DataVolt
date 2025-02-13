import sys


class ETLBase:
    def extract(self):
        raise NotImplementedError("Extract method not implemented")

    def transform(self, data):
        raise NotImplementedError("Transform method not implemented")

    def load(self, data):
        raise NotImplementedError("Load method not implemented")

    def run(self):
        data = self.extract()
        data = self.transform(data)
        self.load(data)


def main():
    if len(sys.argv) == 4:
        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]
        print('Extracting data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        etl = ETLBase()
        messages = etl.extract()
        categories = etl.extract()
        df = messages.merge(categories, on='id')
        print('Transforming data...')
        df = etl.transform(df)
        print('Loading data to database...\n    DATABASE: {}'.format(database_filepath))
        etl.load(df)
        print('Data loaded to database')
    else:
        print('Please provide the filepaths of the messages and categories '
              'datasets as the first and second argument respectively, as '
              'well as the filepath of the database to save the cleaned data '
              'to as the third argument. \n\nExample: python process_data.py '
              'disaster_messages.csv disaster_categories.csv '
              'DisasterResponse.db')

if __name__ == '__main__':
    main()
