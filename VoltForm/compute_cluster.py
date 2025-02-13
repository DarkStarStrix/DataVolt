from VoltForm.base import Plugin
import boto3

class ComputeClusterPlugin(Plugin):
    def __init__(self):
        self.config = None

    def configure(self, config: dict):
        self.config = config

    def execute(self):
        ec2 = boto3.resource('ec2', region_name=self.config['region'])
        instances = ec2.create_instances(
            ImageId='ami-0c55b159cbfafe1f0',
            InstanceType=self.config['instance_type'],
            MinCount=self.config['node_count'],
            MaxCount=self.config['node_count']
        )
        return instances
