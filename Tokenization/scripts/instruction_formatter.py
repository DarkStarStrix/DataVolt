# Tokenization/pretraining/instruction_formatter.py

class InstructionFormatter:
    @staticmethod
    def format_sample(sample):
        """
        Formats a sample dict with 'instruction', 'input', and 'output' fields.
        This is a placeholder; customize as needed for your data.
        """
        instruction = sample.get("instruction") or sample.get("title") or sample.get("domain_tag", "")
        input_ = sample.get("input") or sample.get("abstract") or sample.get("full_text") or sample.get("text")
        output = sample.get("output") or ""
        return {
            "instruction": instruction.strip(),
            "input": (input_ or "").strip(),
            "output": output.strip(),
        }
