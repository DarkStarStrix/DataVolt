from VoltForm.base import Plugin


class ETLPipelinePlugin(Plugin):
    def __init__(self):
        self.config = None

    def configure(self, config: dict):
        self.config = config

    def execute(self):
        return f"ETL pipeline {self.config['name']} executed"