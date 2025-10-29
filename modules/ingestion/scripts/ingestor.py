import logging
import pandas as pd
import requests

logging.basicConfig(level=logging.INFO)

class DataIngestor:
    def ingest(self, source, source_type="file", **kwargs):
        try:
            if source_type == "file":
                return self._ingest_file(source, **kwargs)
            elif source_type == "database":
                return self._ingest_database(source, **kwargs)
            elif source_type == "api":
                return self._ingest_api(source, **kwargs)
            elif source_type == "web":
                return self._ingest_web(source, **kwargs)
            else:
                raise ValueError(f"Unknown source_type: {source_type}")
        except Exception as e:
            logging.error(f"Ingestion failed for {source_type}: {e}")
            return None

    def _ingest_file(self, path, **kwargs):
        ext = path.split('.')[-1].lower()
        if ext in ["csv"]:
            return pd.read_csv(path, **kwargs)
        elif ext in ["json"]:
            return pd.read_json(path, **kwargs)
        elif ext in ["xlsx"]:
            return pd.read_excel(path, **kwargs)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

    def _ingest_database(self, conn_str, query=None, **kwargs):
        import sqlalchemy
        engine = sqlalchemy.create_engine(conn_str)
        if not query:
            raise ValueError("Query must be provided for database ingestion.")
        return pd.read_sql(query, engine, **kwargs)

    def _ingest_api(self, url, params=None, headers=None, **kwargs):
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()

    def _ingest_web(self, url, **kwargs):
        from bs4 import BeautifulSoup
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
