from enum import Enum

class Domain(Enum):
    PHYSICS = "[PHYS]"
    BIOLOGY = "[BIO]"
    MATERIALS = "[MAT]"

class SectionType(Enum):
    HYPOTHESIS = "[HYP]"
    METHOD = "[METHOD]"

# Token limits
MIN_WORDS = 20
MAX_TOKENS = 1024
MAX_TOTAL_TOKENS = 512

# Instructions
HYPOTHESIS_INSTRUCTION = "Generate a scientific hypothesis."
METHOD_INSTRUCTION = "Generate a scientific methodology."

def get_domain_tag(domain_text: str) -> str:
    domain_map = {
        "physics": Domain.PHYSICS.value,
        "biology": Domain.BIOLOGY.value,
        "materials": Domain.MATERIALS.value
    }
    return domain_map.get(domain_text.lower(), Domain.PHYSICS.value)

def get_section_tag(section_text: str) -> str:
    section_map = {
        "hypothesis": SectionType.HYPOTHESIS.value,
        "method": SectionType.METHOD.value
    }
    return section_map.get(section_text.lower(), SectionType.HYPOTHESIS.value)
