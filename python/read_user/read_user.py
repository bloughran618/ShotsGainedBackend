import json
import traceback

import boto3

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
        primary_key = f'USER#{user_name}'
        response = table.query(
            KeyConditionExpression=Key('PK').eq(primary_key)
        )

        # Check if the item was found
        items = response.get('Items')
        if items:
            print(f'found items: {items}')
            return {
                'statusCode': 200,
                'body': json.dumps(
                    {'message': 'Username found', 'record': items},
                    cls=DecimalEncoder
                )
            }
        else:
            print('Item not found')
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Username not found', 'userName': user_name}),
            }

    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Malformed input, does not include userName',
                'input': body
            }),
        }

    except Exception as e:
        print(f'Error reading user {user_name}: ', traceback.format_exc())
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Failure reading the user: {str(e)}',
                'event': event
            }),
        }