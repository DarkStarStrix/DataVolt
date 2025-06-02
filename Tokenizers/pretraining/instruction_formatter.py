from typing import Dict
from Tokenizers.label_tokens import (
    get_domain_tag, get_section_tag,
    HYPOTHESIS_INSTRUCTION, METHOD_INSTRUCTION
)

class InstructionFormatter:
    def format_sample(self, sample: Dict) -> Dict:
        # Add domain and section tags
        domain_tag = get_domain_tag(sample.get("domain", ""))
        section_tag = get_section_tag(sample.get("section", ""))

        # Choose instruction based on section
        section = sample.get("section", "").lower()
        if "hypothesis" in section:
            instruction = HYPOTHESIS_INSTRUCTION
        elif "method" in section:
            instruction = METHOD_INSTRUCTION
        else:
            instruction = "Please answer the following based on the provided context."

        # Format input and output
        formatted_input = f"{domain_tag} {section_tag} {sample.get('input', '')}".strip()
        formatted_output = sample.get("output", "")

        return {
            "instruction": instruction,
            "input": formatted_input,
            "output": formatted_output,
            "domain": sample.get("domain", ""),
            "section": sample.get("section", "")
        }