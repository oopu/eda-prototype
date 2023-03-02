'''
Entrypoint for the application and Pulumi.
Most of the action is under packages. See /ttc
'''
import pulumi
import ttc
from utils.autotagging import register_auto_tags

# Automatically inject tags in subsequent resources based on
#  the project and stack name
config = pulumi.Config()
register_auto_tags({
    "company_name:Project": pulumi.get_project(),
    "company_name:Stack": pulumi.get_stack()
})

# Set up fixtures.
ttc.setup()
