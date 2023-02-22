import pulumi

import fixtures
from utils.autotagging import register_auto_tags

# Automatically inject tags in subsequent resources based on the project and stack name
config = pulumi.Config()
register_auto_tags({
    "user:Project": pulumi.get_project(),
    "user:Stack": pulumi.get_stack()
})

# Set up fixtures.
fixtures.setup_all()
