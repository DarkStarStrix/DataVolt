import boto3

def provision_compute_cluster(config):
    ec2 = boto3.resource('ec2', region_name=config['region'])
    instances = ec2.create_instances(
        ImageId='ami-0c55b159cbfafe1f0',
        InstanceType=config['instance_type'],
        MinCount=1,
        MaxCount=config['count']
    )
    return instances
