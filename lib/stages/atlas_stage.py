from constructs import Construct
from aws_cdk import Stage

from lib.config.environments import EnvironmentConfig
from lib.stacks.infra_stack import InfraStack

class AtlasStage(Stage):


    def __init__(
            self,
            scope: Construct,
            id: str,
            config: EnvironmentConfig,
            env_name: str,
            **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        self.infra = InfraStack(self, "Infra", config=config, env_name=env_name)