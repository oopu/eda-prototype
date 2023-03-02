import pulumi


def register_auto_tags(auto_tags):
    '''
    Registers a global stack transformation that merges a set of tags
    with any explicitly-added ones
    '''
    pulumi.runtime.register_stack_transformation(
        lambda args: auto_tag(args, auto_tags)
    )


def auto_tag(args, auto_tags):
    '''Applies the given tags to the resource properties if applicable.'''
    # This works with most AWS resources in Pulumi but autoscaling groups.
    # This uses primarily serverless resources, so this shouldn't come up.
    # See the following URL for more info:
    # https://www.pulumi.com/registry/packages/aws/api-docs/autoscaling/group/#tags_python
    if hasattr(args.resource, "tags"):
        args.props['tags'] = {**(args.props['tags'] or {}), **auto_tags}
        return pulumi.ResourceTransformationResult(args.props, args.opts)
