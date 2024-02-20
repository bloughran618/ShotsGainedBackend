import json
import logging

import shots_gained_common as sgc


def lambda_handler(event, context):
    # expecting event like
    # {
    #   from: {distance: 450, type: TEE},
    #   to: {distance: 115, type: FAIRWAY}
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
                'error': 'Malformed event body, does not look like # {from: {distance: 450, type: TEE}, to: {distance: 115, type: FAIRWAY}}',
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


# eventual tests
# print(lookup_shot_gained(450, "Tee"))
# # print(lookup_shot_gained(450, "House"))
# print(lookup_shot_gained(115, "Fairway"))
# print(lookup_shot_gained(10, "Green"))
# print(lookup_shot_gained(900, "ROUGH"))
#
# print(get_shot_gained(450, "Tee", 115, "Fairway"))
# print(get_shot_gained(115, "fairway", 10, "GREEN"))
# print(get_shot_gained(10, "Green", 0, "asdf"))
