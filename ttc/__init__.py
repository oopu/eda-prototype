'''This package is for infra and functions specific to the TTC domain'''
import json
import pulumi
import pulumi_aws as aws

from utils.autotagging import register_auto_tags


def setup():
    '''Implements all infrastructure changes for modules in this package'''

    #  Tag all of these with the domain
    register_auto_tags({
        'company_name:Domain': 'ttc'
    })

    # Fetch configs namespaced to "aws" from current stack .yml
    config = pulumi.Config()

    # Create the gateway...
    client_gateway = aws.apigatewayv2.Api(
        "Client Gateway",
        protocol_type="HTTP"
    )

    # ... and the stage. We'll add routes later
    stage = aws.apigatewayv2.Stage(
        "stage",
        api_id=client_gateway.id,
        name=pulumi.get_stack(),
        auto_deploy=True
    )

    # Create the event bus
    ttc_bus = aws.cloudwatch.EventBus("ttc_bus")

    # Allow the gateway full access to the bus
    gateway_eventbridge_role = aws.iam.Role(
        "gateway_eventbridge_role",
        assume_role_policy=json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "apigateway.amazonaws.com",
                    },
                },
            ],
        }),
        managed_policy_arns=[
            "arn:aws:iam::aws:policy/AmazonEventBridgeFullAccess"
        ]
    )

    # Create integration between the gateway and the bus
    integration = aws.apigatewayv2.Integration(
        "integration",
        api_id=client_gateway.id,
        integration_type="AWS_PROXY",
        integration_subtype="EventBridge-PutEvents",
        credentials_arn=gateway_eventbridge_role.arn,
        request_parameters={
            "EventBusName": ttc_bus.name.apply(lambda name: name),
            "Source": "firebase_events",
            "DetailType": "some_detail_type",
            "Detail": "$request.body"
        }
    )

    firebase_events_route = aws.apigatewayv2.Route(
        "firebase_events_route",
        api_id=client_gateway.id,
        route_key="POST /firebase_events",
        target=integration.id.apply(lambda id: f"integrations/{id}")
    )

    # Rule for consuming TTC bus events
    starter_rule = aws.cloudwatch.EventRule(
        "starter_rule",
        event_bus_name=ttc_bus.name,
        event_pattern=json.dumps({
            "source": ["firebase_events"]
        })
    )

    # Execution role to use for Lambda functions
    lambda_role = aws.iam.Role(
        "lambda_role",
        assume_role_policy=json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Action": "sts:AssumeRole",
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com",
                },
            }],
        }),
        managed_policy_arns=[
            aws.iam.ManagedPolicy.AWS_LAMBDA_BASIC_EXECUTION_ROLE
        ]
    )

    # Lets Lambdas log to Cloudwatch
    lambda_logging_policy = aws.iam.RolePolicy(
        "lambda-logging-policy",
        role=lambda_role.id,
        policy=json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "arn:aws:logs:*:*:*"
            }]
        })
    )

    # Actually define the Lambda
    lambda_event_consumer = aws.lambda_.Function(
        "lambda_event_consumer",
        role=lambda_role.arn,
        runtime=config.require("lambda_runtime"),
        handler="lambda_event_consumer.consume_event",
        code=pulumi.FileArchive("./ttc/functions")
    )

    # Integrate the Lambda with the rule above for the bus
    demo_lambda_target = aws.cloudwatch.EventTarget(
        "demo_lambda_target",
        arn=lambda_event_consumer.arn,
        rule=starter_rule.name,
        event_bus_name=ttc_bus.name
    )

    # Let the bus actually invoke the Lambda
    invoke_lambda_permission = aws.lambda_.Permission(
        "invoke_lambda_permission",
        action="lambda:InvokeFunction",
        principal="events.amazonaws.com",
        function=lambda_event_consumer.arn,
        source_arn=starter_rule.arn
    )

    pulumi.export("client_gateway_url", stage.invoke_url)
    pulumi.export("demo_endpoint", firebase_events_route.route_key)
