import json
import traceback

import boto3

dynamodb = boto3.resource('dynamodb')
table_name = 'shotsgained-table'
table = dynamodb.Table(table_name)


def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body'))
        primary_key = f"USER#{body['userName']}"
        secondary_key = f"PROFILE#{body['userName']}"
        item = {
            'PK': primary_key,
            'SK': secondary_key,
            'name': body['name'],
            'stats': {},
        }
    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Malformed event body, either does not include userName or name',
                'input': body
            }),
        }

    try:
        user_name = body.get('userName')
        response = table.get_item(
            Key={
                'PK': primary_key,
                'SK': secondary_key,
            }
        )

        # Check if the username already exists
        if 'Item' in response:
            print('Username already exists:', user_name)
            return {
                'statusCode': 409,
                'body': json.dumps({'message': 'Username already exists', 'userName': user_name}),
            }

        # Write the new user to the table if it doesn't already exist
        response = table.put_item(Item=item)
        print('PutItem succeeded:', response)
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'User added to DB successfully',
                'input': item
            }),
        }
    except Exception as e:
        print(f'Error creating user {user_name}:', traceback.format_exc())
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Failure putting item into DB: {str(e)}',
                'event': event
            }),
        }
