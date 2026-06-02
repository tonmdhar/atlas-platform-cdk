from dataclasses import dataclass
from typing import List

@dataclass
class EnvironmentConfig:
    account: str
    region: str
    vpc_cidr: str
    azs: List[str]
    private_subnets: List[str]
    public_subnets: List[str]
    single_nat_gateway: bool
    node_instance_types: List[str]
    node_desired_size: int
    node_max_size: int
    node_min_size: int
    cluster_name: str

ENVIRONMENTS: dict[str, EnvironmentConfig] = {
    "beta": EnvironmentConfig(
        account="619759452722",
        region="us-east-1",
        vpc_cidr="10.10.0.0/16",
        azs=["us-east-1a", "us-east-1b"],
        private_subnets=["10.10.1.0/24", "10.10.2.0/24"],
        public_subnets=["10.10.101.0/24", "10.10.102.0/24"],
        single_nat_gateway=True,
        node_instance_types=["t3.medium"],
        node_desired_size=2,
        node_max_size=3,
        node_min_size=1,
        cluster_name="atlas-platform-beta",
    ),
    "gamma": EnvironmentConfig(
        account="619759452722",
        region="us-east-1",
        vpc_cidr="10.20.0.0/16",
        azs=["us-east-1a", "us-east-1b"],
        private_subnets=["10.20.1.0/24", "10.20.2.0/24"],
        public_subnets=["10.20.101.0/24", "10.10.102.0/24"],
        single_nat_gateway=True,
        node_instance_types=["t3.large"],
        node_desired_size=2,
        node_max_size=3,
        node_min_size=1,
        cluster_name="atlas-platform-gamma",
    ),
    "prod": EnvironmentConfig(
        account="619759452722",
        region="us-east-1",
        vpc_cidr="10.30.0.0/16",
        azs=["us-east-1a", "us-east-1b", "us-east-1c"],
        private_subnets=["10.30.1.0/24", "10.30.2.0/24", "10.30.3.0/24"],
        public_subnets=["10.30.101.0/24", "10.30.102.0/24", "10.30.103.0/24"],
        single_nat_gateway=False,
        node_instance_types=["t3.large"],
        node_desired_size=3,
        node_max_size=6,
        node_min_size=3,
        cluster_name="atlas-platform-prod",
    )
}
