from VoltForm.base import Plugin
import boto3

class StoragePlugin(Plugin):
    def __init__(self):
        self.config = None

    def configure(self, config: dict):
        self.config = config

    def execute(self):
        s3 = boto3.client('s3', region_name=self.config['region'])
        s3.create_bucket(Bucket=self.config['bucket_name'])
        return f"Bucket {self.config['bucket_name']} created"
