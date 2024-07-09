from _decimal import Decimal

import boto3
import json
import moto
import unittest

import sys
sys.path.append('../../python/shots_gained_common/layer/python/lib/python3.9/site-packages')

from python.add_hole.add_hole import lambda_handler


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        return super().default(o)


@moto.mock_aws
class TestLambdaHandler(unittest.TestCase):
    test_hole = [
        {
            'type': 'tee',
            'distance': 450
        },
        {
            'type': 'fairway',
            'distance': 115,
        },
        {
            'type': 'green',
            'distance': 10,
        }
    ]

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

        existing_round = {
            'PK': 'USER#test_user',
            'SK': 'ROUND#06/18/2023-test_course',
            'date': '06/18/2023',
            'course': 'test_course',
            'holes': []
        }
        self.table.put_item(Item=existing_round)

    def tearDown(self):
        self.table.delete()

    def test_lambda_handler_invalid_event(self):
        event = {
            'body': json.dumps({
                'userName': 'test_user',
                'round': '06/18/2023-test_course'
            })
        }
        context = {}

        response = lambda_handler(event, context)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Malformed event body', response['body'])

    def test_lambda_handler_round_not_found(self):
        event = {
            'body': json.dumps({
                'userName': 'test_user',
                'round': 'round-not-found',
                'shots': self.test_hole
            },
                cls=DecimalEncoder
            )
        }
        context = {}

        response = lambda_handler(event, context)
        self.assertEqual(response['statusCode'], 409)
        self.assertIn('Round does not exist', response['body'])

    def test_lambda_handler_shots_empty(self):
        event = {
            'body': json.dumps({
                'userName': 'test_user',
                'round': '06/18/2023-test_course',
                'shots': []
            })
        }
        context = {}

        response = lambda_handler(event, context)
        self.assertEqual(response['statusCode'], 404)
        self.assertIn('No shots found in request', response['body'])

    def test_lambda_handler_success(self):
        event = {
            'body': json.dumps({
                'userName': 'test_user',
                'round': '06/18/2023-test_course',
                'shots': self.test_hole
            })
        }
        context = {}

        response = lambda_handler(event, context)
        self.assertEqual(response.get('statusCode'), 200)
        self.assertIn('New hole added to round', response.get('body'))

        round = self.table.get_item(
            Key={
                'PK': 'USER#test_user',
                'SK': 'ROUND#06/18/2023-test_course'
            }
        )
        print(f'round: {round}')
        hole = round.get('Item').get('holes')[0]
        self.assertEqual(hole[0].get('shots_gained'), Decimal('0.33'))
        self.assertEqual(hole[1].get('shots_gained'), Decimal('0.23'))
        self.assertEqual(hole[2].get('shots_gained'), Decimal('0.61'))


if __name__ == '__main__':
    unittest.main()
