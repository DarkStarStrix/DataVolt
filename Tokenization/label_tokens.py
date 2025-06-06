# Tokenization/label_tokens.py

# Domain tags
DOMAIN_TAGS = {
    "physics": "[PHYS]",
    "biology": "[BIO]",
    "materials": "[MAT]",
    "education": "[GEN]",
}

# Task tags
TASK_TAGS = {
    "hypothesis": "[HYP]",
    "method": "[MTH]",
    "experiment": "[EXP]",
}

# Section tags (for further granularity, e.g., for long-context or future models)
SECTION_TAGS = {
    "abstract": "[ABSTRACT]",
    "introduction": "[INTRO]",
    "results": "[RESULTS]",
    "discussion": "[DISCUSSION]",
    "conclusion": "[CONCLUSION]",
    "method": "[MTH]",
    "experiment": "[EXP]",
}

# Routing tags
ROUTING_TAGS = {
    "general": "[GEN]",
    "specific": "[SPEC]",
}

# Token/word limits for validation and filtering
MIN_WORDS = 8
MAX_TOKENS = 1024
MAX_TOTAL_TOKENS = 327680000  # Example: 325M tokens

# Token targets for different corpus types
TOKEN_TARGETS = {
    "warm_start": 100_000_000,
    "scientific": 225_000_000,
    "instruction": 30_000_000,
    "default": 325_000_000,
}

def build_tag_string(
    domain: str,
    task: str = None,
    section: str = None,
    routing: str = "general",
    subdomain: str = None
) -> str:
    """
    Build a tag string for a sample, e.g. [PHYS][HYP][GEN] or [BIO][MTH][SPEC: Genomics]
    """
    tags = []
    if domain in DOMAIN_TAGS:
        tags.append(DOMAIN_TAGS[domain])
    if task in TASK_TAGS:
        tags.append(TASK_TAGS[task])
    if section in SECTION_TAGS:
        tags.append(SECTION_TAGS[section])
    if routing == "general":
        tags.append(ROUTING_TAGS["general"])
    elif routing == "specific" and subdomain:
        tags.append(f"[SPEC:{subdomain}]")
    return "".join(tags)
