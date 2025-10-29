import json

class IOUtils:
    def read(self, path):
        if path.endswith('.json'):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()

    def write(self, path, data):
        if path.endswith('.json'):
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(str(data))
