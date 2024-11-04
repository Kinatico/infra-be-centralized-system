from aws_cdk import (
    Stack,
    aws_s3 as s3,
)
from constructs import Construct


class VPCStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, pr_number: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        s3.Bucket(self, "Bucket", bucket_name=f"bucket{pr_number}", versioned=True)