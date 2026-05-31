from constructs import Construct
from aws_cdk import (
    aws_ec2 as ec2,
)
from lib.config.environments import EnvironmentConfig

class VpcConstruct(Construct):
    def __init__(
            self, scope: Construct, id:str, config: EnvironmentConfig) -> None:
        super().__init__(scope, id)

        nat_gateways = 1 if config.single_nat_gateway else len(config.azs)

        self.vpc = ec2.Vpc(
            self,
            "Vpc",
            ip_addresses=ec2.IpAddresses.cidr(config.vpc_cidr),
            availability_zones=config.azs,
            nat_gateways=nat_gateways,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                )
            ],
            restrict_default_security_group=True,
        )