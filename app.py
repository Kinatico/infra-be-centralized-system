#!/usr/bin/env python3
import os

import aws_cdk as cdk

from infrastructure.vpc_stack import VPCStack


app = cdk.App()
pr_number = os.getenv('PR_NUMBER') if os.getenv('PR_NUMBER') else ""
VPCStack(app, f"VPCStack{pr_number}", pr_number=pr_number)

app.synth()