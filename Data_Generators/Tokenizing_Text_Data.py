import nltk
from nltk.tokenize import word_tokenize, RegexpTokenizer

nltk.download ('punkt')


def tokenize_text_and_numbers(text):
    number_tokenizer = RegexpTokenizer (r'\d+')
    number_tokens = number_tokenizer.tokenize (text)

    text_tokens = word_tokenize (text)

    tokens = number_tokens + text_tokens
    return tokens


text = "This is an example sentence with numbers 123 and 456."
tokens = tokenize_text_and_numbers (text)
print (tokens)
