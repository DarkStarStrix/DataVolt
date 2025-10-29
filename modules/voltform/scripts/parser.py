import yaml

def parse_voltform(config_file):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config
