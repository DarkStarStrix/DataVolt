import yaml
from pathlib import Path

from modules.voltform.scripts.Monitoring import MonitoringPlugin

class Main:
    @staticmethod
    def main(config_file):
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)

        monitoring = MonitoringPlugin()
        monitoring.configure(config)
        return 'Success'

if __name__ == '__main__':
    example_config = Path(__file__).resolve().parents[1] / "data" / "Voltform_example.yaml"
    Main.main(str(example_config))
