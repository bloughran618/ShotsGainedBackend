import traceback

import boto3
import json

from boto3.dynamodb.conditions import Key
from decimal import Decimal


dynamodb = boto3.resource('dynamodb')
table_name = 'shotsgained-table'
table = dynamodb.Table(table_name)


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        return super().default(o)


def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body'))
        user_name = body['userName']
        round_name = body['round']
        primary_key = f"USER#{user_name}"
        round_key = f'ROUND#{round_name}'
        profile_key = f'PROFILE#{user_name}'

    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Malformed event body, either does not include userName or round',
                'input': body
            }),
        }

    try:
        response = table.get_item(
            Key={
                'PK': primary_key,
                'SK': round_key
            }
        )

        if 'Item' not in response:
            print(f'Round {round_name} does not exist for user {user_name}')
            return {
                'statusCode': 409,
                'body': json.dumps({'message': 'Round does not exist', 'userName': user_name, 'round': round_name}),
            }

        holes = response.get('Item').get('holes')
        if not holes:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'message': 'No holes for round',
                    'userName': user_name,
                    'round': round_name,
                    'holes': holes})
            }

        # aggregate round data for the round
        shots_stats = {
            'tee': 0,
            'fairway': 0,
            'rough': 0,
            'sand': 0,
            'recovery': 0,
            'green': 0
        }
        shotsgained_stats = {
            'tee': 0,
            'fairway': 0,
            'rough': 0,
            'sand': 0,
            'recovery': 0,
            'green': 0
        }
        try:
            for hole in holes:
                for shot in hole:
                    shot_type = shot['type']
                    shots_stats[shot_type] += 1
                    shotsgained_stats[shot_type] += shot['shots_gained']
        except Exception as e:
            return {
                'statusCode': 409,
                'body': json.dumps({'message': f'Failed aggregating holes: {e}', 'holes': holes})
            }
        round_stats = {'shots': shots_stats, 'shotsgained': shotsgained_stats}
        print(f'round stats for {round_name}: {round_stats}')

        response = table.update_item(
            Key={'PK': primary_key, 'SK': round_key},
            UpdateExpression='SET stats = :stats, finished = :finished',
            ExpressionAttributeValues={
                ':stats': round_stats,
                ':finished': True,
            },
            ReturnValues='UPDATED_NEW'
        )

        # aggregate all round stats for the user
        shots_stats = {
            'tee': 0,
            'fairway': 0,
            'rough': 0,
            'sand': 0,
            'recovery': 0,
            'green': 0
        }
        shotsgained_stats = {
            'tee': 0,
            'fairway': 0,
            'rough': 0,
            'sand': 0,
            'recovery': 0,
            'green': 0
        }

        response = table.query(
            KeyConditionExpression=(
                Key('PK').eq(primary_key) &
                Key('SK').begins_with('ROUND#')
            )
        )
        if 'Items' in response:
            all_rounds = response.get('Items')
            for finished_round in all_rounds:
                if finished_round.get('stats'):
                    finished_round_stats = finished_round.get('stats')
                    round_shots_stats = finished_round_stats.get('shots')
                    round_shotsgained_stats = finished_round_stats.get('shotsgained')
                    for key, value in round_shots_stats.items():
                        shots_stats[key] += value
                    for key, value in round_shotsgained_stats.items():
                        shotsgained_stats[key] += value

            rounds_stats = {'shots': shots_stats, 'shotsgained': shotsgained_stats}
            print(f'All rounds stats for user {user_name}: {rounds_stats}')

            response = table.update_item(
                Key={'PK': primary_key, 'SK': profile_key},
                UpdateExpression='SET stats = :stats',
                ExpressionAttributeValues={
                    ':stats': rounds_stats
                },
                ReturnValues='UPDATED_NEW'
            )

            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': f'Round finished for {round_name}',
                    'round_stats': round_stats
                },
                    cls=DecimalEncoder
                )
            }
        else:
            print(f'No rounds found for user: {user_name}')
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'No rounds found', 'userName': user_name}),
            }

        return {
            'statusCode': 200,
            'body': json.dumps({'message': f'Round {round_name} completed for user {user_name} successfully!'}),
        }

    except Exception as e:
        print(f'Error completing round {round_name} for user {user_name}:', traceback.format_exc())
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Failure completing round: {str(e)}',
                'event': event
            }),
        }
