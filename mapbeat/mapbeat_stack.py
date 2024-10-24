from aws_cdk import (
    Stack,
    Tags,
    aws_lambda as _lambda,
    aws_apigatewayv2 as apigatewayv2,
    aws_apigatewayv2_integrations as integrations,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_iam as iam,
    aws_s3 as s3,
    CfnOutput
)
from constructs import Construct
from pathlib import Path

class MapbeatStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, *, sns_topic_arn: str = None, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Tag the entire stack
        Tags.of(self).add("Project", "Mapbeat")

        # Import existing SNS topic if ARN is provided, otherwise create new one
        if sns_topic_arn:
            topic = sns.Topic.from_topic_arn(self, "ExistingTopic", sns_topic_arn)
        else:
            topic = sns.Topic(
                self, "NotificationTopic",
                display_name="WebsocketNotifications",
                topic_name="websocket-notifications"
            )

        # Import bucket
        bucket = s3.Bucket.from_bucket_name(self, "ExistingBucket", 'real-changesets')

        # Create Lambda function from external code
        lambda_path = Path(__file__).parent.parent / "lambda"
        websocket_lambda = _lambda.Function(
            self, "WebSocketLambda",
            runtime=_lambda.Runtime.NODEJS_18_X,
            handler="index.handler",
            code=_lambda.Code.from_asset(str(lambda_path))
        )

        # Grant the Lambda function read access to the S3 bucket
        bucket.grant_read(websocket_lambda)

        # Create WebSocket API
        websocket_api = apigatewayv2.WebSocketApi(
            self, "WebSocketApi"
        )

        # Create Lambda integration
        websocket_integration = integrations.WebSocketLambdaIntegration(
            "WebSocketIntegration",
            handler=websocket_lambda
        )

        # Add routes
        websocket_api.add_route(
            "$connect",
            integration=websocket_integration
        )
        websocket_api.add_route(
            "$disconnect",
            integration=websocket_integration
        )

        # Create stage
        stage = apigatewayv2.WebSocketStage(
            self, "WebSocketStage",
            web_socket_api=websocket_api,
            stage_name="prod",
            auto_deploy=True
        )

        # Grant permissions for API Gateway to invoke Lambda
        websocket_lambda.add_permission(
            "WebSocketPermission",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            source_arn=f"arn:aws:execute-api:{self.region}:{self.account}:{websocket_api.api_id}/*"
        )

        # Subscribe Lambda to SNS topic
        topic.add_subscription(
            subscriptions.LambdaSubscription(websocket_lambda)
        )

        # Grant permissions for Lambda to manage WebSocket connections
        websocket_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["execute-api:ManageConnections"],
                resources=[
                    f"arn:aws:execute-api:{self.region}:{self.account}:{websocket_api.api_id}/{stage.stage_name}/POST/*"
                ]
            )
        )

        # Set the WebSocket endpoint URL in Lambda environment
        websocket_lambda.add_environment(
            "WEBSOCKET_API_ENDPOINT",
            f"{websocket_api.api_id}.execute-api.{self.region}.amazonaws.com/{stage.stage_name}"
        )

        # Output values
        CfnOutput(
            self, "WebSocketURL",
            description="WebSocket URL",
            value=f"wss://{websocket_api.api_id}.execute-api.{self.region}.amazonaws.com/{stage.stage_name}"
        )
        CfnOutput(
            self, "SNSTopicARN",
            description="SNS Topic ARN",
            value=topic.topic_arn
        )
