import json
from collections import Counter
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from transformers import AutoTokenizer

from Tokenizers.Build_tokenizer import QLoRAPreprocessor
from Tokenizers.entropy_ranker import EntropyRanker
from Tokenizers.pretraining.dataset_stats import DatasetAnalyzer
from Tokenizers.pretraining.instruction_formatter import InstructionFormatter

def get_sample_text(sample):
    return (
        sample.get('text') or
        sample.get('content') or
        sample.get('full_text') or
        sample.get('excerpt') or
        ''
    )

def eda_report(samples, out_dir: Path, prefix: str, report_lines: List[str]):
    data = {
        'domain': [s.get('domain', 'unknown') for s in samples],
        'section': [s.get('section', 'unknown') for s in samples],
        'word_count': [len(str(get_sample_text(s)).split()) for s in samples],
    }
    df = pd.DataFrame(data)

    # Stats for a report
    report_lines.append(f"\n--- {prefix} EDA Report ---")
    report_lines.append(str(df.describe(include='all')))
    report_lines.append("\nDomain distribution:\n" + str(df['domain'].value_counts()))
    report_lines.append("\nSection distribution:\n" + str(df['section'].value_counts()))

    # Plots
    out_dir.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(10, 4))
    sns.countplot(x='domain', data=df)
    plt.title('Domain Distribution')
    plt.tight_layout()
    plt.savefig(out_dir / f"{prefix}_domain_distribution.png")
    plt.close()

    plt.figure(figsize=(10, 4))
    sns.countplot(x='section', data=df)
    plt.title('Section Distribution')
    plt.tight_layout()
    plt.savefig(out_dir / f"{prefix}_section_distribution.png")
    plt.close()

    plt.figure(figsize=(10, 4))
    sns.histplot(df['word_count'], bins=30, kde=True)
    plt.title('Word Count Distribution')
    plt.tight_layout()
    plt.savefig(out_dir / f"{prefix}_word_count_distribution.png")
    plt.close()

class ScientificDataProcessor:
    def __init__(self, model_name: str = "facebook/opt-350m"):
        self.preprocessor = QLoRAPreprocessor(model_name)
        self.analyzer = DatasetAnalyzer(model_name)
        self.formatter = InstructionFormatter()
        self.ranker = EntropyRanker()
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    def read_jsonl(self, input_path: str) -> List[Dict]:
        with open(input_path, 'r', encoding='utf-8') as f:
            return [json.loads(line) for line in f if line.strip()]

    def analyze_dataset(self, samples: List[Dict], report_lines: List[str], prefix: str):
        stats = self.analyzer.get_dataset_stats(samples)
        domain_counts = Counter(sample.get('domain', 'unknown') for sample in samples)
        section_counts = Counter(sample.get('section', 'unknown') for sample in samples)
        report_lines.append(f"\n--- {prefix} Dataset Statistics ---")
        report_lines.append(f"Total samples: {stats['total_samples']}")
        report_lines.append(f"Average tokens per sample: {stats['avg_tokens']:.2f}")
        report_lines.append(f"Average words per sample: {stats['avg_words']:.2f}")
        report_lines.append(f"Domain distribution: {dict(domain_counts)}")
        report_lines.append(f"Section distribution: {dict(section_counts)}")
        return stats

    def process_dataset(self, input_path: str, output_path: str):
        print(f"Processing JSONL dataset: {input_path}")
        samples = self.read_jsonl(input_path)
        if not samples:
            print("No valid samples found in input file")
            return

        report_lines = []
        eda_dir = Path("eda_plots")
        report_path = Path("eda_report.txt")

        # Original dataset analysis and EDA
        self.analyze_dataset(samples, report_lines, "Original")
        eda_report(samples, eda_dir, "original", report_lines)

        # Formatting
        formatted_samples = [self.formatter.format_sample(sample) for sample in samples]

        # Entropy ranking
        entropy_scores = [
            (self.ranker.calculate_entropy(get_sample_text(sample)), sample)
            for sample in formatted_samples
        ]
        ranked_samples = [
            sample for _, sample in sorted(entropy_scores, key=lambda x: x[0], reverse=True)
        ]
        report_lines.append(f"\nSamples after entropy filtering: {len(ranked_samples)}")

        # Validation
        valid_samples = [
            sample for sample in ranked_samples
            if self.preprocessor.validate_sample(sample)
        ]

        # Save processed samples
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            for sample in valid_samples:
                f.write(json.dumps(sample) + '\n')
        report_lines.append(f"\nProcessed {len(valid_samples)} samples saved to {output_path}")

        # Processed dataset analysis and EDA
        self.analyze_dataset(valid_samples, report_lines, "Processed")
        eda_report(valid_samples, eda_dir, "processed", report_lines)

        # Write a report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        print(f"EDA plots saved in {eda_dir}, report saved as {report_path}")

if __name__ == "__main__":
    processor = ScientificDataProcessor()
    processor.process_dataset(
        "C:/Users/kunya/PycharmProjects/DataVolt/Tokenizers/combined_scientific_papers.jsonl",
        "scientific_instruction_processed.jsonl"
    )