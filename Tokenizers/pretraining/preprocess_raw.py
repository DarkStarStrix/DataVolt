import json
from pathlib import Path
from Tokenizers.pretraining.instruction_formatter import InstructionFormatter

def preprocess_raw(input_path: str, output_path: str):
    formatter = InstructionFormatter()
    with open(input_path, 'r', encoding='utf-8') as infile:
        samples = [json.loads(line) for line in infile]
    formatted = [formatter.format_sample(sample) for sample in samples]
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for sample in formatted:
            outfile.write(json.dumps(sample) + '\n')

if __name__ == "__main__":
    # Example usage
    preprocess_raw(
        "Tokenizers/combined_scientific_papers.json",
        "Tokenizers/pretraining/formatted_scientific_papers.jsonl"
    )