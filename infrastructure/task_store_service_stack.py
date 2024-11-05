from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecr as ecr,
    aws_ecs as ecs,
    Stack,
    aws_iam as iam,
    aws_logs as logs,
    aws_elasticloadbalancingv2 as elbv2, Duration, CfnOutput
)
from constructs import Construct

class TaskStoreServiceStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, pr_number: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get the VPC by its VPC ID
        vpc = ec2.Vpc.from_lookup(self, "kinatico-vpc", vpc_id="vpc-0122d00502378e5a7")

        # Create a Security Group for the Application Load Balancer (ALB)
        security_group_alb = ec2.SecurityGroup(
            self, "security-group-task-store-alb",
            vpc=vpc,
            description="Allow traffic from VPC Lattice to ALB",
        )

        # Inbound rule: Allow traffic from VPC Lattice (specific IPs or Security Groups) to the ALB
        security_group_alb.add_ingress_rule(
            ec2.Peer.any_ipv4(),  # Replace with specific IP address or Security Group for VPC Lattice if needed
            ec2.Port.tcp(80),  # Change to HTTPS (443) if ALB uses HTTPS
            "Allow HTTP traffic from VPC Lattice to ALB"
        )

        # Egress rule: Allow ALB to send traffic to ECS tasks
        security_group_alb.add_egress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80),  # Port of ECS service or container port
            "Allow traffic from ALB to ECS tasks"
        )

        # Create a Security Group for the ECS Service to allow connections from the ALB
        security_group_ecs_service = ec2.SecurityGroup(
            self, "security-group-ecs-task-store-service",
            vpc=vpc,
            description="Allow traffic from ALB to ECS tasks",
        )

        # Inbound rule: Allow traffic from the ALB to ECS tasks
        security_group_ecs_service.add_ingress_rule(
            security_group_alb,  # Allow traffic only from the ALB
            ec2.Port.tcp(80),  # Must match the port used by the container
            "Allow traffic from ALB to ECS tasks"
        )

        # Create an ECS Cluster
        ecs_cluster = ecs.Cluster(self, "task-store-cluster", vpc=vpc)

        # Get the ECR repository by its name
        repository = ecr.Repository.from_repository_name(self, "infra-be-centralized-system-repository", "infra-be-centralized-system")

        # Add an IAM Role for the ECS Task
        task_role = iam.Role(self, "ecs-task-store-execution-role",
                             assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
                             managed_policies=[
                                 iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy"),
                                 iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryFullAccess")
                             ])

        # Create a Task Definition for ECS
        task_definition = ecs.FargateTaskDefinition(self, "task-store-task-definition", task_role=task_role, execution_role=task_role)
        task_definition.add_container(
            "task-store-container",
            image=ecs.ContainerImage.from_ecr_repository(repository, tag="latest"),
            memory_limit_mib=512,
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="infra-be-centralized-system",
                log_group=logs.LogGroup(self, "task-store-log-group", retention=logs.RetentionDays.ONE_DAY),
            )
        ).add_port_mappings(
            ecs.PortMapping(container_port=80)
        )

        # Create the ECS Service in a Private Subnet
        service = ecs.FargateService(
            self, "task-store-ecs-service",
            cluster=ecs_cluster,
            task_definition=task_definition,
            desired_count=1,
            security_groups=[security_group_ecs_service],
            vpc_subnets={"subnet_type": ec2.SubnetType.PRIVATE_ISOLATED}
        )

        # Tạo Application Load Balancer
        load_balancer = elbv2.ApplicationLoadBalancer(
            self, "task-store-alb",
            vpc=vpc,
            internet_facing=False,
        )

        # Tạo Listener cho ALB
        listener = load_balancer.add_listener("Listener", port=80)

        # Thêm ECS Service vào Listener
        listener.add_targets("ECS", port=80, targets=[service],
                             health_check=elbv2.HealthCheck(
                                 path="/health",
                                 interval=Duration.seconds(30),
                                 timeout=Duration.seconds(5),
                                 healthy_threshold_count=2,
                                 unhealthy_threshold_count=2
                             ))

        # Output Load Balancer DNS
        CfnOutput(self, "task-store-load-balancer-dns", value=load_balancer.load_balancer_dns_name, description="The DNS of the load balancer")
