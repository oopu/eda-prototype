# eda-prototype
A generic prototype for a primarily event-driven platform based on AWS using serverless technologies.

# Features
* An API gateway(v2) instance and stage with its URL and available routes exported (see `pulumi up` or `pulumi stack output` output)
* An event bus with a single rule for a single Lambda function that echoes received messages from the given source to CloudWatch logs
* Automatic resource tagging (for resources that support it) by domain, environment and Pulumi project ID

# Taking it Further
* You should consider adding a reusable component for creating an EventBridge Pipe that reads from SQS. This pattern will come up at least once in the future. See https://www.pulumi.com/docs/intro/concepts/resources/components/ for how to do so.
* If you want to add infrastructure specific to another domain, like ecom's event bus and related functions, create a new Python package under something like /ecom and follow the same pattern under /ttc. Pulumi can attempt to import existing resources to the active stack with `pulumi import`.
* Configure new stacks for your deployment environments with `pulumi init`
* Add some tests to the packages with `pytest` and `behave` to get some CI going for your Lambda functions