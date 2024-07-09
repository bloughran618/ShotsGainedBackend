import json
import logging

import shots_gained_common as sgc


def lambda_handler(event, context):
    # expecting event like
    # {
    #   'from': {'distance': 450, 'type': 'TEE'},
    #   'to': {'distance': 115, 'type': 'FAIRWAY'}
    # }
    logging.info(f"the event: {event}")
    try:
        body = json.loads(event.get('body'))
        from_distance = body['from']['distance']
        from_type = body['from']['type']
        to_distance = body['to']['distance']
        to_type = body['to']['type']
    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': "Malformed event body, does not look like # {'from': {'distance': 450, 'type': 'TEE'}, "
                         "'to': {'distance': 115, 'type': 'FAIRWAY'}}",
                'input': body
            }),
        }

    shots_gained = sgc.get_shot_gained(from_distance, from_type, to_distance, to_type)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'shots_gained': shots_gained
        }),
    }
