import random

class SyntheticGenerator:
    def generate(self, schema):
        # schema: dict of {field: (type, range/choices)}
        record = {}
        for field, (ftype, param) in schema.items():
            if ftype == int:
                record[field] = random.randint(*param)
            elif ftype == float:
                record[field] = random.uniform(*param)
            elif ftype == str:
                record[field] = random.choice(param)
        return record
