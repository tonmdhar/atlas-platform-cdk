from constructs import Construct
from aws_cdk import (
    aws_iam as iam,
    aws_eks as eks,
    aws_dynamodb as dynamodb,
)


class IrsaConstruct(Construct):

    def __init__(
            self,
            scope: Construct,
            id: str,
            cluster: eks.Cluster,
            table: dynamodb.Table,
            namespace_manifest,
            namespace: str = "atlas",
            service_account_name: str = "atlas-api-sa",
    ) -> None:
        super().__init__(scope, id)

        self.service_account = cluster.add_service_account(
            "AtlasApiServiceAccount",
            name=service_account_name,
            namespace=namespace,
        )
        self.service_account.node.add_dependency(namespace_manifest)

        table.grant_read_write_data(self.service_account)
