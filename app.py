#!/usr/bin/env python3
import aws_cdk as cdk

from lib.config.environments import ENVIRONMENTS
from lib.stacks.infra_stack import InfraStack

app = cdk.App()
env_name = app.node.try_get_context("env") or "beta"
config = ENVIRONMENTS[env_name]

InfraStack(
    app,
    f"AtlasPlatform-{env_name.capitalize()}-Infra",
    config=config,
    env=cdk.Environment(
        account=config.account,
        region=config.region,
    )
)

app.synth()
