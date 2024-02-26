import json
import boto3

dynamodb = boto3.resource('dynamodb')
table_name = 'shotsgained-table'
table = dynamodb.Table(table_name)


def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body'))
        primary_key = f"USER#{body['userName']}"
        item = {
            'PK': primary_key,
            'name': body['name'],
            'rounds': [],
            'friends': [],
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
        print('Error putting item:', str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Failure putting item into DB',
                'event': event
            }),
        }
