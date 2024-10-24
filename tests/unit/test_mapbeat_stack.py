import aws_cdk as core
import aws_cdk.assertions as assertions

from mapbeat.mapbeat_stack import MapbeatStack

# example tests. To run these tests, uncomment this file along with the example
# resource in mapbeat/mapbeat_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = MapbeatStack(app, "mapbeat")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
