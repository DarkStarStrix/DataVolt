class Plugin:
    def configure(self, config):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError
