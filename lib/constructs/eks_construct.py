from aws_cdk.lambda_layer_kubectl_v31 import KubectlV31Layer
from constructs import Construct
from aws_cdk import (
    aws_eks as eks,
    aws_ec2 as ec2,
    aws_iam as iam,
    Size,
)

from lib.config.environments import EnvironmentConfig

class EksConstruct(Construct):

    def __init__(
            self, scope: Construct, id: str, config: EnvironmentConfig, vpc: ec2.Vpc) -> None:
        super().__init__(scope, id)

        self.cluster = eks.Cluster(
            self,
            "Cluster",
            cluster_name=config.cluster_name,
            version=eks.KubernetesVersion.V1_31,
            kubectl_layer=KubectlV31Layer(self, "KubectlLayer"),
            vpc=vpc,
            vpc_subnets=[ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)],
            endpoint_access=eks.EndpointAccess.PRIVATE,
            default_capacity=0,
            authentication_mode=eks.AuthenticationMode.API_AND_CONFIG_MAP,
            kubectl_memory=Size.mebibytes(512),
        )

        # Create the atlas namespace (must exist before ServiceAccounts)
        self.namespace = self.cluster.add_manifest(
            "AtlasNamespace",
            api_version="v1",
            kind="Namespace",
            metadata={"name": "atlas"},
        )

        self.nodegroup = self.cluster.add_nodegroup_capacity(
            "ManagedNodeGroup",
            instance_types=[ec2.InstanceType(it) for it in config.node_instance_types],
            desired_size=config.node_desired_size,
            max_size=config.node_max_size,
            min_size=config.node_min_size,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
        )
