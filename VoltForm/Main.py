import yaml
from VoltForm.Monitoring import MonitoringPlugin

class Main:
    @staticmethod
    def main(config_file):
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)

        monitoring = MonitoringPlugin()
        monitoring.configure(config)
        return 'Success'

if __name__ == '__main__':
    Main.main('C:/Users/kunya/PycharmProjects/DataVolt/VoltForm/Voltform_example.yaml')
