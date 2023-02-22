'''This directory is for common infrastructure shared by service domains.'''
import fixtures.client_gateway as client_gateway
import fixtures.eventbridge as eventbridge

def setup_all():
    '''Implements all infrastructure changes for modules in this package'''
    client_gateway.setup()
    eventbridge.setup()
