from constructs import Construct
from aws_cdk import Stack

from lib.config.environments import EnvironmentConfig
from lib.constructs.vpc_construct import VpcConstruct
from lib.constructs.eks_construct import EksConstruct

class InfraStack(Stack):
    def __init__(
            self, scope: Construct, id: str, config: EnvironmentConfig, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.vpc = VpcConstruct(self, "Vpc", config=config)
        self.eks = EksConstruct(self, "Eks", config=config, vpc=self.vpc.vpc)