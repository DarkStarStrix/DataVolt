import logging
from pathlib import Path

from modules.market_mind.scripts import (
    scrape_reddit_json,
    save_data,
    preprocess_data,
    upload_embeddings,
    query_vector,
    train_model,
    dashboard_app,
)


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW_PATH = DATA_DIR / "dataengineering_posts.csv"
PREPROCESSED_PATH = DATA_DIR / "preprocessed_data.csv"

def data_ingestion():
    logging.info("Starting data ingestion...")
    df = scrape_reddit_json("dataengineering", limit=50)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    save_data(df, RAW_PATH)
    logging.info("Data ingestion completed.")

def text_processing():
    logging.info("Starting text processing...")
    preprocess_data(RAW_PATH, PREPROCESSED_PATH)
    logging.info("Text processing completed.")

def vector_database():
    logging.info("Starting vector database operations...")
    upload_embeddings(PREPROCESSED_PATH)
    logging.info("Vector database operations completed.")

def sql_query_optimization():
    logging.info("Starting SQL query and optimization...")
    query_vector(PREPROCESSED_PATH)
    logging.info("SQL query and optimization completed.")

def transformer_model():
    logging.info("Starting transformer model training...")
    train_model(PREPROCESSED_PATH)
    logging.info("Transformer model training completed.")

def dashboard():
    logging.info("Starting dashboard...")
    dashboard_app.run()
    logging.info("Dashboard is running.")

def run_workflow():
    try:
        data_ingestion()
        text_processing()
        vector_database()
        sql_query_optimization()
        transformer_model()
        dashboard()
    except Exception as e:
        logging.error(f"Workflow failed: {e}")

if __name__ == "__main__":
    run_workflow()
