# eda-prototype
A generic prototype for a primarily event-driven platform based on AWS using serverless technologies.

# Features
* An API gateway(v2) instance and stage with its URL and available routes exported (see `pulumi up` or `pulumi stack output` output)
* An event bus with a single rule for a single Lambda function that echoes received messages from the given source to CloudWatch logs
* Automatic resource tagging (for resources that support it) by domain, environment and Pulumi project ID

# Getting Started

## Prerequisites
This repo uses Python 3.7 for application code and Pulumi for developing infrastructure as code.
For more information on setting these up, see:
* [Python getting started docs](https://www.python.org/about/gettingstarted/)
* [Pulumi getting started docs](https://www.pulumi.com/docs/get-started/)

You'll also need to have an AWS account with CLI access. See:
* [AWS CLI Quick Setup docs](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html)

### Pulumi Backend
In this project, use of Pulumi involves use of their [Pulumi Service backend](https://www.pulumi.com/docs/intro/pulumi-service/), which means you'll need an account there as well. This service manages stack changes that you trigger from the CLI (or that we trigger via later CI/CD operations) and provides a nice UI to view changes to stacks.

## Environment Setup
Follow the above prerequisite steps, then run `pulumi up`. This should run `pip` locally to download dependencies to your local virtual environment and then stand up the infrastructure in your configured AWS account (if you choose to do so). 

**Be wary of deploying to prod!** Pulumi will tell you what it's going to deploy with a preview before you tell it to proceed, and it will error on logical name collisions with existing resources. Nevertheless, it's safer to deploy into a separate AWS account until you know what you're doing.

# Taking it Further
* You should consider adding a reusable component for creating an EventBridge Pipe that reads from SQS. This pattern will come up at least once in the future. See https://www.pulumi.com/docs/intro/concepts/resources/components/ for how to do so.
* Consider refactoring /ttc/__init__.py to not be so flat, and maybe create an enumeration of event sources and event schema definitions to prevent discrepancies
* If you want to add infrastructure specific to another domain, like ecom's event bus and related functions, create a new Python package under something like /ecom and follow the same pattern under /ttc. Pulumi can attempt to import existing resources to the active stack with `pulumi import`.
* Configure new stacks for your deployment environments with `pulumi init`
* Add some tests to the packages with `pytest` and `behave` to get some CI going for your Lambda functions