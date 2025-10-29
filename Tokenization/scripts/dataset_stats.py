from collections import Counter
from typing import Dict, List

import numpy as np
from transformers import AutoTokenizer


class DatasetAnalyzer:
    def __init__(self, model_name: str = "facebook/opt-350m"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
    def analyze_sample(self, sample: Dict) -> Dict:
        tokens = self.tokenizer.encode(str(sample))
        return {
            "token_count": len(tokens),
            "word_count": len(str(sample).split()),
            "has_abstract": bool(sample.get("abstract")),
            "has_content": bool(sample.get("full_text") or sample.get("excerpt")),
            "has_section": bool(sample.get("section_type")),
            "domain": sample.get("domain_tag", "unknown")
        }
    
    def get_dataset_stats(self, samples: List[Dict]) -> Dict:
        stats = []
        domains = Counter()
        sections = Counter()
        
        for sample in samples:
            sample_stats = self.analyze_sample(sample)
            stats.append(sample_stats)
            domains[sample_stats["domain"]] += 1
            sections[sample.get("section_type", "unknown")] += 1
            
        return {
            "total_samples": len(samples),
            "avg_tokens": np.mean([s["token_count"] for s in stats]),
            "avg_words": np.mean([s["word_count"] for s in stats]),
            "domain_distribution": dict(domains),
            "section_distribution": dict(sections)
        }
