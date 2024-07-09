import boto3
import json
import moto

import unittest
from python.create_round.create_round import lambda_handler


@moto.mock_aws
class TestLambdaHandler(unittest.TestCase):

    def setUp(self):
        self.table_name = 'shotsgained-table'
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        self.table = self.dynamodb.create_table(
            TableName=self.table_name,
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

        existing_user = {
            'PK': 'USER#test_user',
            'SK': 'PROFILE#test_user',
            'name': 'Test User',
            'stats': {}
        }
        self.table.put_item(Item=existing_user)

    def tearDown(self):
        self.table.delete()

    def test_lambda_handler_invalid_event(self):
        event = {
            'body': json.dumps({
                'userName': 'test_user',
                'date': '06/18/2023'
            })
        }
        context = {}

        response = lambda_handler(event, context)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Malformed event body', response['body'])

    def test_lambda_handler_successful(self):
        event = {
            'body': json.dumps({
                'userName': 'test_user',
                'date': '06/18/2023',
                'course': 'test_course'
            })
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 200)
        self.assertIn('New round added to DB successfully', response['body'])

    def test_lambda_handler_existing_round(self):
        # Add an existing round to the table
        existing_round = {
            'PK': 'USER#test_user',
            'SK': 'ROUND#06/18/2023-test_course',
            'date': '06/18/2023',
            'course': 'test_course',
            'holes': []
        }
        self.table.put_item(Item=existing_round)

        event = {
            'body': json.dumps({
                'userName': 'test_user',
                'date': '06/18/2023',
                'course': 'test_course'
            })
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 409)
        self.assertIn('Round exists for username', response['body'])


if __name__ == '__main__':
    unittest.main()
