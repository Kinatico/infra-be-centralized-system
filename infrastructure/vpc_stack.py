from aws_cdk import (
    aws_ec2 as ec2,
    Stack,
)
from constructs import Construct


class VPCStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, pr_number: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a VPC has 1 Private Subnet and 0 NAT Gateway
        vpc = ec2.Vpc(self, "kinatico-vpc",
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

        # Setup VPC Endpoint for ECR API and ECR DKR
        ecr_api_endpoint = ec2.InterfaceVpcEndpoint(self, 'ECRVpcEndpoint',
                                                    vpc=vpc,
                                                    service=ec2.InterfaceVpcEndpointAwsService.ECR,
                                                    private_dns_enabled=True)

        ecr_docker_endpoint = ec2.InterfaceVpcEndpoint(self, 'ECRDockerVpcEndpoint',
                                                       vpc=vpc,
                                                       service=ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER,
                                                       private_dns_enabled=True)

        # Setup Gateway VPC Endpoint for S3
        s3_endpoint = ec2.GatewayVpcEndpoint(self, 'S3GatewayEndpoint',
                                             vpc=vpc,
                                             service=ec2.GatewayVpcEndpointAwsService.S3,
                                             subnets=[{"subnet_type": ec2.SubnetType.PRIVATE_ISOLATED}])

        # Setup Interface VPC Endpoint for CloudWatch Logs
        cloudwatch_logs_endpoint = ec2.InterfaceVpcEndpoint(self, 'CloudWatchLogsVpcEndpoint',
                                                            vpc=vpc,
                                                            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS,
                                                            private_dns_enabled=True)

        # sqs_endpoint = ec2.InterfaceVpcEndpoint(self, 'SQSVpcEndpoint',
        #                                         vpc=vpc,
        #                                         service=ec2.InterfaceVpcEndpointAwsService.SQS,
        #                                         private_dns_enabled=True)