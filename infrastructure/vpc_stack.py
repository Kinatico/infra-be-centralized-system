from aws_cdk import (
    aws_ec2 as ec2,
    Stack,
)
from constructs import Construct


class VPCStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, pr_number: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a VPC has 1 Private Subnet and 0 NAT Gateway
        vpc = ec2.Vpc(self, "biwoco-VPC",
                      max_azs=2,
                      nat_gateways=0,
                      subnet_configuration=[
                          ec2.SubnetConfiguration(
                              name="PrivateSubnet",
                              subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                              cidr_mask=24,
                          )
                      ]
                      )