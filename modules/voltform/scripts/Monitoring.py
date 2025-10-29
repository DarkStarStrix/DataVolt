
class MonitoringPlugin:
    def __init__(self):
        self.config = None

    def configure(self, config):
        self.config = config
        print(f"Configuring MonitoringPlugin with config: {self.config}")

    def execute(self):
        print(f"Executing MonitoringPlugin with config: {self.config}")
        if 'logs' in self.config:
            print(f"'logs' key found in config: {self.config['logs']}")
            if 'provider' in self.config['logs']:
                print(f"Logs provider found: {self.config['logs']['provider']}")
                return f"Monitoring enabled with provider {self.config['logs']['provider']}"
            else:
                print("Missing 'provider' key in 'logs' configuration")
                raise KeyError("Missing 'provider' key in 'logs' configuration")
        else:
            print("Missing 'logs' key in configuration")
            raise KeyError("Missing 'logs' key in configuration")
