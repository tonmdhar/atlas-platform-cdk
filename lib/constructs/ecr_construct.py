from constructs import Construct
from aws_cdk import (
    aws_ecr as ecr,
    Duration,
    RemovalPolicy,
)

class EcrConstruct(Construct):

    def __init__(self, scope: Construct, id: str, env_name: str) -> None:
        super().__init__(scope, id)

        self.repository = ecr.Repository(
            self,
            "Repository",
            repository_name=f"atlas-platform-{env_name}",
            removal_policy=RemovalPolicy.DESTROY if env_name != "prod" else RemovalPolicy.RETAIN,
            empty_on_delete=True if env_name != "prod" else False,
            lifecycle_rules=[
                ecr.LifecycleRule(
                    description="Remove untagged after 1 day",
                    tag_status=ecr.TagStatus.UNTAGGED,
                    max_image_age=Duration.days(1),
                    rule_priority=1,
                ),
                ecr.LifecycleRule(
                    description="Keep last 10 images",
                    max_image_count=10,
                    rule_priority=2,
                ),
            ]
        )
