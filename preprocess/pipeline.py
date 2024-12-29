class PreprocessingPipeline:
    def __init__(self, steps):
        self.steps = steps

    def process(self, data):
        result = data.copy ()
        for step in self.steps:
            result = step.transform (result)
        return result
