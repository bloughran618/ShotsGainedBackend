import boto3
from decimal import Decimal
import json
import traceback

dynamodb = boto3.resource('dynamodb')
table_name = 'shotsgained-table'
table = dynamodb.Table(table_name)

import shots_gained_common as sgc


def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body'))
        user_name = body['userName']
        round_name = body['round']
        shots = body['shots']
        primary_key = f"USER#{user_name}"
        secondary_key = f'ROUND#{round_name}'

    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Malformed event body, either does not include round, shots or userName',
                'input': body
            }),
        }

    try:
        response = table.get_item(
            Key={
                'PK': primary_key,
                'SK': secondary_key
            }
        )

        # Check if there is a round for the given username
        if 'Item' not in response:
            print(f'Round {round_name} does not exist for user {user_name}')
            return {
                'statusCode': 409,
                'body': json.dumps({'message': 'Round does not exist', 'userName': user_name, 'round': round_name}),
            }

        # populate shots with shotsgained for each hole
        if len(shots) == 0:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'No shots found', 'shots': shots}),
            }
        for shot_ind, shot in enumerate(shots):
            if shot_ind == len(shots) - 1:
                shots_gained = sgc.get_shot_gained(
                    shot.get('distance'),
                    shot.get('type'),
                    0,
                    'green'
                )
            else:
                shots_gained = sgc.get_shot_gained(
                    shot.get('distance'),
                    shot.get('type'),
                    shots[shot_ind + 1].get('distance'),
                    shots[shot_ind + 1].get('type')
                )
            shot['shots_gained'] = shots_gained
        print(f'the populated shots: {shots}')

        response = table.update_item(
            Key={'PK': primary_key, 'SK': secondary_key},
            UpdateExpression=f'SET holes = list_append(if_not_exists(holes, :empty_list), :shots)',
            ExpressionAttributeValues={
                ':shots': [json.loads(json.dumps(shots), parse_float=Decimal)],
                ':empty_list': [],
            },
            ReturnValues='UPDATED_NEW'
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'New hole added to round {round_name} for user {user_name} successfully',
                'hole': shots
            }),
        }

    except Exception as e:
        print('Error adding hole: ', traceback.format_exc())
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Failure adding hole {shots} to round {round_name}: {str(e)}',
                'event': event
            }),
        }
