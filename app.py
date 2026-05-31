#!/usr/bin/env python3
import aws_cdk as cdk

from lib.config.environments import ENVIRONMENTS
from lib.stacks.pipeline_stack import PipelineStack

app = cdk.App()

pipeline_env = ENVIRONMENTS["beta"]

PipelineStack(
    app,
    "AtlasPlatform-Pipeline",
    env=cdk.Environment(
        account=pipeline_env.account,
        region=pipeline_env.region,
    )
)

app.synth()
