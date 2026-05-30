import aws_cdk as core
import aws_cdk.assertions as assertions

from atlas_platform_cdk.atlas_platform_cdk_stack import AtlasPlatformCdkStack

# example tests. To run these tests, uncomment this file along with the example
# resource in atlas_platform_cdk/atlas_platform_cdk_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AtlasPlatformCdkStack(app, "atlas-platform-cdk")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
