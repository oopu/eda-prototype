import json
import pulumi
import pulumi_aws as aws
import pulumi_aws_apigateway as apigateway
from util.autotagging import register_auto_tags

# Automatically inject tags based on the project and stack name
config = pulumi.Config()
register_auto_tags({
    "user:Project": pulumi.get_project(),
    "user:Stack": pulumi.get_stack()
})

# An execution role to use for the Lambda function
role = aws.iam.Role("role", 
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
    managed_policy_arns=[aws.iam.ManagedPolicy.AWS_LAMBDA_BASIC_EXECUTION_ROLE])

# A Lambda function to invoke
fn = aws.lambda_.Function("fn",
    runtime="python3.9",
    handler="handler.handler",
    role=role.arn,
    code=pulumi.FileArchive("./function"))

# A REST API to route requests to HTML content and the Lambda function
api = apigateway.RestAPI("api",
  routes=[
    apigateway.RouteArgs(path="/", local_path="www"),
    apigateway.RouteArgs(path="/date", method=apigateway.Method.GET, event_handler=fn)
  ])

# The URL at which the REST API will be served.
pulumi.export("url", api.url)
