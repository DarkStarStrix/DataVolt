# Tokenization/pretraining/instruction_formatter.py

class InstructionFormatter:
    @staticmethod
    def format_sample(sample):
        """
        Formats a sample dict with 'instruction', 'input', and 'output' fields.
        This is a placeholder; customize as needed for your data.
        """
        # Ensure required fields exist
        instruction = sample.get("instruction", "")
        input_ = sample.get("input", "")
        output = sample.get("output", "")
        return {
            "instruction": instruction.strip(),
            "input": input_.strip(),
            "output": output.strip(),
        }
