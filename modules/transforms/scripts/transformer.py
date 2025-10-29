class Transformer:
    def transform(self, data):
        # Example: uppercase all string elements in a list
        return [x.upper() if isinstance(x, str) else x for x in data]
