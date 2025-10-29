import math
from typing import List, Dict, Optional, Callable

class EntropyRanker:
    """
    Scores and filters text samples by Shannon entropy of their token distribution.
    Used to remove low-information or repetitive samples from scientific corpora.
    """

    def __init__(self, entropy_threshold: float = 3.5, tokenizer: Optional[Callable[[str], List[str]]] = None):
        """
        Args:
            entropy_threshold: Minimum entropy required to keep a sample.
            tokenizer: Function to tokenize text. Defaults to whitespace split.
        """
        self.entropy_threshold = entropy_threshold
        self.tokenizer = tokenizer or (lambda x: x.split())

    @staticmethod
    def shannon_entropy(tokens: List[str]) -> float:
        """Compute Shannon entropy for a list of tokens."""
        if not tokens:
            return 0.0
        freq = {}
        for t in tokens:
            freq[t] = freq.get(t, 0) + 1
        total = len(tokens)
        entropy = 0.0
        for count in freq.values():
            p = count / total
            entropy -= p * math.log(p, 2)
        return entropy

    def score_sample(self, text: str) -> float:
        """Tokenize and score a text sample by entropy."""
        tokens = self.tokenizer(text)
        return self.shannon_entropy(tokens)

    def is_explanatory(self, text: str) -> bool:
        """Return True if sample passes an entropy threshold."""
        return self.score_sample(text) >= self.entropy_threshold

    def filter_samples(self, samples: List[Dict], text_key: str = "text") -> List[Dict]:
        """Filter a list of dict samples, keeping only those above a threshold."""
        return [s for s in samples if self.is_explanatory(s.get(text_key, ""))]

    def rank_samples(self, samples: List[Dict], text_key: str = "text", top_k: Optional[int] = None) -> List[Dict]:
        """
        Rank samples by entropy, descending. Optionally return only top_k.
        """
        scored = [
            (self.score_sample(s.get(text_key, "")), s)
            for s in samples
        ]
        scored.sort(reverse=True, key=lambda x: x[0])
        ranked = [s for _, s in scored if _ >= self.entropy_threshold]
        if top_k is not None:
            ranked = ranked[:top_k]
        return ranked