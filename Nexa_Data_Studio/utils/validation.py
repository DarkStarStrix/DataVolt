def validate_num_tokens(num_tokens):
    if not (1000 <= num_tokens <= 500000):
        raise ValueError("Number of tokens must be between 1,000 and 500,000.")
    return num_tokens

def validate_num_rows(num_rows):
    if not (100 <= num_rows <= 100000):
        raise ValueError("Number of rows must be between 100 and 100,000.")
    return num_rows

