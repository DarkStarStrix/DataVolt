import joblib


class ModelExporter:
    def __init__(self, file_path):
        self.file_path = file_path

    def save_model(self, model):
        joblib.dump (model, self.file_path)
