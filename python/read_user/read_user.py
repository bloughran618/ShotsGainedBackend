import json
import boto3

dynamodb = boto3.resource('dynamodb')
table_name = 'shotsgained-table'
table = dynamodb.Table(table_name)


def lambda_handler(event, context):
    try:
        user_name = event['userName']
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
                'body': json.dumps({'message': 'Item found', 'item': item}),
            }
        else:
            print('Item not found')
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Item not found', 'item': user_name}),
            }

    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Malformed input, does not include userName'}),
        }

    except Exception as e:
        print('Error reading item:', str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'}),
        }