import boto3
import pandas as pd


class S3Loader:
    def __init__(self, bucket_name, file_key, aws_access_key_id, aws_secret_access_key):
        self.bucket_name = bucket_name
        self.file_key = file_key
        self.s3_client = boto3.client (
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

    def load_data(self):
        obj = self.s3_client.get_object (Bucket=self.bucket_name, Key=self.file_key)
        return pd.read_csv (obj ['Body'])
