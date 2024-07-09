import boto3
import json
import moto

import unittest
from python.create_user.create_user import lambda_handler


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

    def tearDown(self):
        self.table.delete()

    def test_lambda_handler_invalid_event(self):
        event = {
            'body': json.dumps({
                'name': 'Test User'
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
                'name': 'Test User'
            })
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 200)
        self.assertIn('User added to DB successfully', response['body'])

    def test_lambda_handler_existing_user(self):
        # Add an existing user to the table
        existing_user = {
            'PK': 'USER#test_user',
            'SK': 'PROFILE#test_user',
            'name': 'Test User',
            'stats': {}
        }
        self.table.put_item(Item=existing_user)

        event = {
            'body': json.dumps({
                'userName': 'test_user',
                'name': 'Test User'
            })
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 409)
        self.assertIn('Username already exists', response['body'])


if __name__ == '__main__':
    unittest.main()
