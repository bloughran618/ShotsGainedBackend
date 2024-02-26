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
        primary_key = f"USER#{user_name}"

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
            }
        )

        # Check if the username already exists
        if 'Item' not in response:
            print('Username does not exist:', user_name)
            return {
                'statusCode': 409,
                'body': json.dumps({'message': 'Username does not exist', 'userName': user_name}),
            }

        new_round = [{
            f"{date}-{course}": {
                "date": date,
                "course": course,
                "holes": []
            }
        }]

        # Update the item with the new data
        response = table.update_item(
            Key={"PK": primary_key},
            UpdateExpression="set rounds = list_append(rounds, :n)",
            ExpressionAttributeValues={
                ":n": new_round
            },
            ReturnValues='UPDATED_NEW'  # Optionally, specify the return values
        )

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
                'error': f'Failure putting item into DB',
                'event': event
            }),
        }
