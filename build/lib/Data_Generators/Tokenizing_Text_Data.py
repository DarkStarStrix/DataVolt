import nltk
from nltk.tokenize import word_tokenize, RegexpTokenizer

# Download necessary NLTK data
nltk.download ('punkt')


# Tokenize text and numbers
def tokenize_text_and_numbers(text):
    # Tokenize numbers
    number_tokenizer = RegexpTokenizer (r'\d+')
    number_tokens = number_tokenizer.tokenize (text)

    # Tokenize normal text
    text_tokens = word_tokenize (text)

    # Combine tokens
    tokens = number_tokens + text_tokens
    return tokens


# Example usage
text = "This is an example sentence with numbers 123 and 456."
tokens = tokenize_text_and_numbers (text)
print (tokens)
