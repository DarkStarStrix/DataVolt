# voltform/visualize_and_provision.py
import yaml
from VoltForm import validate_voltform
from VoltForm.engine import provision_compute_cluster

def parse_yaml(config_file):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

def visualize_yaml_as_mermaid(config):
    mermaid_diagram = "graph TD\n"
    mermaid_diagram += "    A[Infrastructure] --> B[Compute Cluster]\n"
    mermaid_diagram += f"    B --> C[Type: {config['infrastructure']['compute_cluster']['type']}]\n"
    mermaid_diagram += f"    B --> D[Region: {config['infrastructure']['compute_cluster']['region']}]\n"
    mermaid_diagram += f"    B --> E[Instance Type: {config['infrastructure']['compute_cluster']['instance_type']}]\n"
    mermaid_diagram += f"    B --> F[Node Count: {config['infrastructure']['compute_cluster']['node_count']}]\n"
    return mermaid_diagram

def provision_infrastructure(config):
    compute_cluster_config = {
        'region': config['infrastructure']['compute_cluster']['region'],
        'instance_type': config['infrastructure']['compute_cluster']['instance_type'],
        'count': config['infrastructure']['compute_cluster']['node_count']
    }
    instances = provision_compute_cluster(compute_cluster_config)
    return instances

def run_workflow(config_file):
    config = parse_yaml(config_file)

    # Validate the configuration
    if validate_voltform(config):
        # Visualize the configuration as a Mermaid diagram
        mermaid_diagram = visualize_yaml_as_mermaid(config)
        print("Mermaid Diagram:\n", mermaid_diagram)

        # Ask user to confirm provisioning
        user_input = input("Do you want to provision the infrastructure? (yes/no): ")
        if user_input.lower() == 'yes':
            instances = provision_infrastructure(config)
            print("Provisioned Instances:", instances)
        else:
            print("Provisioning cancelled.")

if __name__ == '__main__':
    run_workflow('C:/Users/kunya/PycharmProjects/DataVolt/VoltForm/Voltform_example.yaml')
