import pandas as pd
import re

def clean_text(text):
    text = re.sub(r',', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def preprocess_data(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    df['text'] = df['title'].apply(clean_text)
    df['label'] = df['score'].apply(lambda x: 1 if x > 0 else 0)
    df = df[['text', 'label']]
    df.to_csv(output_csv, index=False)

if __name__ == "__main__":
    preprocess_data('dataengineering_posts.csv', 'preprocessed_data.csv')
