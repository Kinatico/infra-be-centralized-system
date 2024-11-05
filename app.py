#!/usr/bin/env python3
import os

import aws_cdk as cdk

from infrastructure.vpc_stack import VPCStack
from infrastructure.task_store_service_stack import TaskStoreServiceStack


app = cdk.App()
pr_number = os.getenv('PR_NUMBER') if os.getenv('PR_NUMBER') else ""
environment = app.node.try_get_context("environments.staging")
account = environment["account"]
region = environment["region"]
env = cdk.Environment(account=account, region=region)

if not pr_number:
    VPCStack(app, f"VPCStack{pr_number}", pr_number=pr_number)

TaskStoreServiceStack(app, f"TaskStoreServiceStack{pr_number}", pr_number=pr_number, env=env)

app.synth()