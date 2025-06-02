from collections import Counter
from math import log2
from typing import List, Dict


class EntropyRanker:
    def __init__(self, min_entropy_threshold: float = 3.0):
        self.min_entropy_threshold = min_entropy_threshold
        
    def calculate_entropy(self, text: str) -> float:
        # Calculate Shannon entropy of the text
        counts = Counter(text.split())
        total = sum(counts.values())
        probs = [count/total for count in counts.values()]
        return -sum(p * log2(p) for p in probs)
    
    def rank_samples(self, samples: List[Dict]) -> List[Dict]:
        # Calculate entropy scores for all samples
        entropy_scores = []
        for sample in samples:
            content = sample.get("input", "") + " " + sample.get("output", "")
            entropy = self.calculate_entropy(content)
            entropy_scores.append((entropy, sample))
            
        # Sort by entropy and filter low-entropy samples
        sorted_samples = [
            sample for entropy, sample in sorted(entropy_scores, reverse=True)
            if entropy >= self.min_entropy_threshold
        ]
        
        return sorted_samples
