from constructs import Construct
from aws_cdk import (
    aws_dynamodb as dynamodb,
    aws_ec2 as ec2,
    RemovalPolicy,
)

class DynamoDbConstruct(Construct):

    def __init__(self, scope: Construct, id: str, env_name: str, vpc: ec2.Vpc) -> None:
        super().__init__(scope, id)

        self.table = dynamodb.Table(
            self,
            "ItemsTable",
            table_name=f"atlas-platform-{env_name}-items",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY if env_name != "prod" else RemovalPolicy.RETAIN,
        )

        # VPC Gateway Endpoint for DynamoDB (free, avoids NAT costs)
        self.vpc_endpoint = vpc.add_gateway_endpoint(
            "DynamoDbEndpoint",
            service=ec2.GatewayVpcEndpointAwsService.DYNAMODB
        )
