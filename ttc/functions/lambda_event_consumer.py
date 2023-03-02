import json


def consume_event(event, context):
    print(json.dumps({
        "source": event["source"],
        "payload": event["detail"]
    }))
