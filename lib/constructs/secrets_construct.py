from constructs import Construct
from aws_cdk import (
    aws_secretsmanager as secretsmanager,
    aws_eks as eks,
    RemovalPolicy,
)

class SecretsConstruct(Construct):

    def __init__(
            self,
            scope: Construct,
            id: str,
            env_name: str,
            cluster: eks.Cluster
    ) -> None:
        super().__init__(scope, id)

        # Create a secret for the application (DB credentials, API keys, etc.)
        self.app_secret = secretsmanager.Secret(
            self,
            "AppSecret",
            secret_name=f"atlas-platform/{env_name}/app-config",
            description=f"Application secrets for atlas-platform-{env_name}",
            removal_policy=RemovalPolicy.DESTROY if env_name != "prod" else RemovalPolicy.RETAIN,
        )

        # ServiceAccount with Secrets Manager read access
        self.service_account = cluster.add_service_account(
            "SecretsServiceAccount",
            name="atlas-secrets-sa",
            namespace="atlas"
        )

        self.app_secret.grant_read(self.service_account)
