
import logging
from Market_Mind import scrape_reddit_json, save_data, preprocess_data, upload_embeddings, query_vector, train_model, dashboard_app


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def data_ingestion():
    logging.info("Starting data ingestion...")
    df = scrape_reddit_json("dataengineering", limit=50)
    save_data(df, "C:/Users/kunya/PycharmProjects/DataVolt/Market_Mind/Data/dataengineering_posts.csv")
    logging.info("Data ingestion completed.")

def text_processing():
    logging.info("Starting text processing...")
    preprocess_data("C:/Users/kunya/PycharmProjects/DataVolt/Market_Mind/Data/dataengineering_posts.csv", "C:/Users/kunya/PycharmProjects/DataVolt/Market_Mind/Data/preprocessed_data.csv")
    logging.info("Text processing completed.")

def vector_database():
    logging.info("Starting vector database operations...")
    upload_embeddings("C:/Users/kunya/PycharmProjects/DataVolt/Market_Mind/Data/preprocessed_data.csv")
    logging.info("Vector database operations completed.")

def sql_query_optimization():
    logging.info("Starting SQL query and optimization...")
    query_vector("C:/Users/kunya/PycharmProjects/DataVolt/Market_Mind/Data/preprocessed_data.csv")
    logging.info("SQL query and optimization completed.")

def transformer_model():
    logging.info("Starting transformer model training...")
    train_model("C:/Users/kunya/PycharmProjects/DataVolt/Market_Mind/Data/preprocessed_data.csv")
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