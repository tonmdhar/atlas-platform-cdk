from constructs import Construct
from aws_cdk import Stack

from lib.config.environments import EnvironmentConfig
from lib.constructs.vpc_construct import VpcConstruct
from lib.constructs.eks_construct import EksConstruct
from lib.constructs.dynamodb_construct import DynamoDbConstruct
from lib.constructs.irsa_construct import IrsaConstruct
from lib.constructs.ecr_construct import EcrConstruct
from lib.constructs.secrets_construct import SecretsConstruct
from lib.constructs.monitoring_construct import MonitoringConstruct

class InfraStack(Stack):
    def __init__(
            self,
            scope: Construct,
            id: str,
            config: EnvironmentConfig,
            env_name: str,
            **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        self.vpc = VpcConstruct(self, "Vpc", config=config)
        self.eks = EksConstruct(self, "Eks", config=config, vpc=self.vpc.vpc)
        self.dynamodb = DynamoDbConstruct(self, "DynamoDb", env_name=env_name, vpc=self.vpc.vpc)
        self.irsa = IrsaConstruct(self, "Irsa", self.eks.cluster, self.dynamodb.table)
        self.irsa.node.add_dependency(self.eks.namespace)

        self.ecr = EcrConstruct(self, "Ecr", env_name=env_name)
        self.secrets = SecretsConstruct(self, "Secrets", env_name=env_name, cluster=self.eks.cluster)
        self.secrets.node.add_dependency(self.eks.namespace)
        self.monitoring = MonitoringConstruct(self, "Monitoring", env_name=env_name, cluster=self.eks.cluster)
