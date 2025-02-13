
import logging

import torch
from transformers import BertTokenizer, BertForSequenceClassification

from Market_Mind.Dashboard import df


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_seo_content(subreddit):
    logging.info("Starting SEO content generation...")

    tokenizer = BertTokenizer.from_pretrained('C:/Users/kunya/PycharmProjects/DataVolt/Market_Mind/Models/sentiment_model')
    model = BertForSequenceClassification.from_pretrained('C:/Users/kunya/PycharmProjects/DataVolt/Models/Market_Mind/sentiment_model')

    articles = []
    for _, row in df.iterrows():
        inputs = tokenizer(row['title'], return_tensors='pt', max_length=512, truncation=True, padding='max_length')
        outputs = model(**inputs)
        seo_content = torch.argmax(outputs.logits, dim=1).item()
        article = f"Title: {row['title']}\nSEO Content: {seo_content}\n\n"
        articles.append(article)

    with open(f"{subreddit}_articles.txt", "w") as f:
        f.writelines(articles)
    logging.info("Article generation completed.")

    return articles

if __name__ == "__main__":
    generate_seo_content("dataengineering")
