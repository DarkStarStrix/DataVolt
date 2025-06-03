import json
from pathlib import Path
from typing import Dict

from transformers import AutoTokenizer

from Tokenization.entropy_ranker import EntropyRanker
from Tokenization.label_tokens import MIN_WORDS, MAX_TOKENS, MAX_TOTAL_TOKENS, TOKEN_TARGETS
from Tokenization.pretraining.dataset_stats import DatasetAnalyzer
from Tokenization.pretraining.instruction_formatter import InstructionFormatter


class QLoRAPreprocessor:
    def __init__(self, model_name: str = "facebook/opt-350m", corpus_type: str = "warm_start"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.analyzer = DatasetAnalyzer(model_name)
        self.formatter = InstructionFormatter()
        self.ranker = EntropyRanker()
        self.token_target = TOKEN_TARGETS[corpus_type]
        self.current_tokens = 0

    def track_tokens(self, text: str) -> bool:
        tokens = self.tokenizer.encode(text)
        self.current_tokens += len(tokens)
        return self.current_tokens <= self.token_target

    def validate_sample(self, sample: Dict) -> bool:
        if not all(k in sample for k in ["instruction", "input", "output"]):
            return False
        total_text = f"{sample['instruction']} {sample['input']} {sample['output']}"
        tokens = self.tokenizer.encode(total_text)
        words = total_text.split()
        return (len(words) >= MIN_WORDS and
                len(tokens) <= MAX_TOKENS and
                len(tokens) <= MAX_TOTAL_TOKENS)

    def process_dataset(self, input_path: str, output_path: str):
        # Load data, skipping blank lines and malformed JSON
        data = []
        with open(input_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Skipping line {i}: {e}")

        # Analyze dataset
        stats = self.analyzer.get_dataset_stats(data)
        print(f"Dataset stats: {stats}")

        # Format samples
        formatted_samples = [
            self.formatter.format_sample(sample)
            for sample in data
        ]

        # Rank and filter samples
        ranked_samples = self.ranker.rank_samples(formatted_samples)

        # Track token count while processing
        valid_samples = []
        for sample in ranked_samples:
            if not self.validate_sample(sample):
                continue
                
            sample_text = f"{sample['instruction']} {sample['input']} {sample['output']}"
            if not self.track_tokens(sample_text):
                break
                
            valid_samples.append(sample)

        # Save to JSONL
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            for sample in valid_samples:
                f.write(json.dumps(sample) + '\n')

        print(f"Processed {len(valid_samples)} samples saved to {output_path}")

if __name__ == "__main__":
    preprocessor = QLoRAPreprocessor()
    preprocessor.process_dataset(
        "C:/Users/kunya/PycharmProjects/DataVolt/Tokenizers/combined_scientific_papers.json",
        "nexa_scientific_instruction_300k.jsonl"
    )
