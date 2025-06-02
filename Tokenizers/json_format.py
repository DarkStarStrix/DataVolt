import json

with open('C:/Users/kunya/PycharmProjects/DataVolt/Tokenizers/combined_scientific_papers.json', 'r', encoding='utf-8') as f:
    data = json.load(f)  # This expects a single JSON array

with open('C:/Users/kunya/PycharmProjects/DataVolt/Tokenizers/combined_scientific_papers.jsonl', 'w', encoding='utf-8') as f:
    for item in data:
        f.write(json.dumps(item) + '\n')