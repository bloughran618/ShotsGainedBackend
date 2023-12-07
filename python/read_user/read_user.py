import json
import boto3

dynamodb = boto3.resource('dynamodb')
table_name = 'shotsgained-table'
table = dynamodb.Table(table_name)


def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body'))
        user_name = body['userName']
        response = table.get_item(
            Key={
                'userName': user_name,
            }
        )

        # Check if the item was found
        if 'Item' in response:
            item = response['Item']
            print('Item found:', item)
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Username found', 'record': item}),
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
        print('Error reading item:', str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'}),
        }