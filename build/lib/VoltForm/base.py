# voltform/plugins/base.py

# voltform/base.py
class Plugin:
    def configure(self, config):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError
