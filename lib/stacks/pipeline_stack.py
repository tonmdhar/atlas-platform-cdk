from constructs import Construct
from aws_cdk import (
    Stack,
    aws_codepipeline_actions as cpactions,
    pipelines,
)

from lib.config.environments import ENVIRONMENTS
from lib.stages.atlas_stage import AtlasStage

class PipelineStack(Stack):

    def __init__(
            self,
            scope: Construct,
            id: str,
            **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # Source: GitHub via CodeStar connection
        source = pipelines.CodePipelineSource.connection(
            "tonmdhar/atlas-platform-cdk",
            "main",
            connection_arn=
                "arn:aws:codeconnections:us-east-1:733508956784:connection/0d9170d0-ca8a-4437-b010-a2c54bd0c04e",
        )

        # Self-mutating pipeline
        pipeline = pipelines.CodePipeline(
            self,
            "Pipeline",
            pipeline_name="AtlasPlatform-Pipeline",
            synth=pipelines.ShellStep(
                "Synth",
                input=source,
                install_commands=[
                    "pip install -r requirements.txt",
                ],
                commands=[
                    "npm cdk synth",
                ],
            ),
        )

        # Stage 1: Beta (auto-promote)
        beta_config = ENVIRONMENTS["beta"]
        pipeline.add_stage(
            AtlasStage(
                self,
                "Beta",
                config=beta_config,
                env_name="beta",
                env={"account": beta_config.account, "region": beta_config.region},
            ),
        )

        # Stage 2: Gamma (auto-promote)
        gamma_config = ENVIRONMENTS["gamma"]
        pipeline.add_stage(
            AtlasStage(
                self,
                "Gamma",
                config=gamma_config,
                env_name="gamma",
                env={"account": gamma_config.account, "region": gamma_config.region},
            ),
        )

        # Stage 3: Prod (manual approval before deploy)
        prod_config = ENVIRONMENTS["prod"]
        pipeline.add_stage(
            AtlasStage(
                self,
                "Prod",
                config=prod_config,
                env_name="prod",
                env={"account": prod_config.account, "region": prod_config.region},
            ),
        )