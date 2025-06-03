class MLModule:
    def train(self, data):
        # Example: pretend to fit a model
        self.model = sum(data) / len(data) if data else None

    def predict(self, data):
        # Example: return the mean as prediction
        return [self.model for _ in data] if hasattr(self, 'model') else [0 for _ in data]
