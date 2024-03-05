import json
import boto3

dynamodb = boto3.resource('dynamodb')
table_name = 'shotsgained-table'
table = dynamodb.Table(table_name)


def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body'))
        date = body['date']
        course = body['course']
        user_name = body['userName']
        round_name = f'{date}-{course}'
        primary_key = f'USER#{user_name}'
        secondary_key = f'ROUND#{round_name}'

    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Malformed event body, either does not include date, course or userName',
                'input': body
            }),
        }

    try:
        response = table.get_item(
            Key={
                'PK': primary_key,
                'SK': secondary_key,
            }
        )

        # Check if username/round combination exists
        if 'Item' in response:
            print(f'Round exists for username {user_name}, course {course} and date {date}')
            return {
                'statusCode': 409,
                'body': json.dumps({
                    'message': 'Round exists for username',
                    'userName': user_name,
                    'round': round_name
                }),
            }

        new_round = {
            'PK': primary_key,
            'SK': secondary_key,
            "date": date,
            "course": course,
            "holes": [],
        }

        response = table.put_item(Item=new_round)
        print('PutItem succeeded:', response)
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'New round added to DB successfully',
                'input': new_round
            }),
        }
    except Exception as e:
        print('Error putting item:', str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Failure putting item into DB: {str(e)}',
                'event': event
            }),
        }
