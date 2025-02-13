# vector_database.py
import pandas as pd
import torch
from pinecone import Pinecone, ServerlessSpec
from transformers import AutoTokenizer, AutoModel


PINECONE_API_KEY = "pcsk_4uiVDA_8cS8qAH9a71LuT5ZcgfiCLhy9FrxnQdZWqbHv71im7VgrXvEeCg7XnqUurVfGsv"

pc = Pinecone(
    api_key=PINECONE_API_KEY,
)

index_name = 'marketmind-index'
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,
        metric='cosine',
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1',
        )
    )
index = pc.Index(index_name)

tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')

def get_embedding(text):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    return embeddings

def upload_embeddings(csv_file):
    df = pd.read_csv(csv_file)
    to_upsert = []
    for i, row in df.iterrows():
        text = row['title']
        vector = get_embedding(text)
        to_upsert.append((str(i), vector.tolist(), {"text": text}))

    index.upsert(vectors=to_upsert)
    print(f"Uploaded {len(to_upsert)} vectors to Pinecone.")

def query_vector(query_text, top_k=5):
    query_vector = get_embedding(query_text)
    results = index.query(vector=query_vector.tolist(), top_k=top_k, include_metadata=True)
    return results

if __name__ == '__main__':
    # Upload embeddings
    upload_embeddings('C:/Users/kunya/PycharmProjects/DataVolt/Market_Mind/dataengineering_posts.csv')

    # Query vector database
    query = "latest trends in data engineering"
    results = query_vector(query)
    for match in results['matches']:
        print(match['metadata']['text'])
        print(f"Similarity: {match['score']:.4f}\n")
