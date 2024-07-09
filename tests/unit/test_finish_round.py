from decimal import Decimal

import boto3
import json
import moto

import unittest
from python.finish_round.finish_round import lambda_handler


@moto.mock_aws
class TestLambdaHandler(unittest.TestCase):

    test_shots = [
        [
            {
                'type': 'tee',
                'distance': 450,
                'shots_gained': round(Decimal(0.33), 2)
            },
            {
                'type': 'fairway',
                'distance': 115,
                'shots_gained': round(Decimal(0.23), 2)
            },
            {
                'type': 'green',
                'distance': 10,
                'shots_gained': round(Decimal(0.61), 2)
            }
        ],
        [
            {
                'type': 'tee',
                'distance': 150,
                'shots_gained': round(Decimal(-0.83), 2)
            },
            {
                'type': 'sand',
                'distance': 40,
                'shots_gained': round(Decimal(0.04), 2)
            },
            {
                'type': 'green',
                'distance': 15,
                'shots_gained': round(Decimal(-0.35), 2)
            },
            {
                'type': 'green',
                'distance': 4,
                'shots_gained': round(Decimal(0.13), 2)
            }
        ],
        [
            {
                'type': 'tee',
                'distance': 399,
                'shots_gained': round(Decimal(-0.79), 2)
            },
            {
                'type': 'recovery',
                'distance': 117,
                'shots_gained': round(Decimal(-0.17), 2)
            },
            {
                'type': 'rough',
                'distance': 72,
                'shots_gained': round(Decimal(0.45), 2)
            },
            {
                'type': 'green',
                'distance': 8,
                'shots_gained': round(Decimal(-0.54), 2)
            },
            {
                'type': 'green',
                'distance': 2,
                'shots_gained': round(Decimal(0.04), 2)
            }
        ]
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

    def tearDown(self):
        self.table.delete()

    def test_lambda_handler_invalid_event(self):
        event = {
            'body': json.dumps({
                'userName': 'test_user'
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
                'round': 'round-not-found'
            })
        }
        context = {}

        response = lambda_handler(event, context)
        self.assertEqual(response['statusCode'], 409)
        self.assertIn('Round does not exist', response['body'])

    def test_lambda_handler_no_holes_found(self):
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
                'round': '06/18/2023-test_course'
            })
        }
        context = {}

        response = lambda_handler(event, context)
        self.assertEqual(response['statusCode'], 404)
        self.assertIn('No holes for round', response['body'])

    def test_lambda_handler_malformed_holes(self):
        existing_round = {
            'PK': 'USER#test_user',
            'SK': 'ROUND#06/18/2023-test_course',
            'date': '06/18/2023',
            'course': 'test_course',
            'holes': [
                [
                    {
                        'type': 'tee'
                    }
                ]
            ]
        }
        self.table.put_item(Item=existing_round)

        event = {
            'body': json.dumps({
                'userName': 'test_user',
                'round': '06/18/2023-test_course'
            })
        }
        context = {}

        response = lambda_handler(event, context)
        self.assertEqual(response['statusCode'], 409)
        self.assertIn('Failed aggregating holes', response['body'])

    def test_lambda_handler_success(self):
        existing_round = {
            'PK': 'USER#test_user',
            'SK': 'ROUND#06/18/2023-test_course',
            'date': '06/18/2023',
            'course': 'test_course',
            'holes': self.test_shots
        }
        self.table.put_item(Item=existing_round)

        event = {
            'body': json.dumps({
                'userName': 'test_user',
                'round': '06/18/2023-test_course'
            })
        }
        context = {}

        response = lambda_handler(event, context)
        response_json = json.loads(response.get('body'))
        shots_stats = response_json.get('round_stats').get('shots')
        shotsgained_stats = response_json.get('round_stats').get('shotsgained')
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('Round finished for', response['body'])
        self.assertEqual(shots_stats.get('tee'), 3)
        self.assertEqual(shots_stats.get('fairway'), 1)
        self.assertEqual(shots_stats.get('rough'), 1)
        self.assertEqual(shots_stats.get('sand'), 1)
        self.assertEqual(shots_stats.get('recovery'), 1)
        self.assertEqual(shots_stats.get('green'), 5)
        self.assertEqual(shotsgained_stats.get('tee'), '-1.29')
        self.assertEqual(shotsgained_stats.get('fairway'), '0.23')
        self.assertEqual(shotsgained_stats.get('rough'), '0.45')
        self.assertEqual(shotsgained_stats.get('sand'), '0.04')
        self.assertEqual(shotsgained_stats.get('recovery'), '-0.17')
        self.assertEqual(shotsgained_stats.get('green'), '-0.11')

    def test_lambda_handler_success_existing_round(self):
        existing_round_stats = {
            'PK': 'USER#test_user',
            'SK': 'ROUND#another_round',
            'date': '06/18/2023',
            'course': 'test_course',
            'holes': [],
            'stats': {
                'shots': {
                    'tee': 1,
                    'fairway': 1,
                    'rough': 0,
                    'sand': 0,
                    'recovery': 0,
                    'green': 1
                },
                'shotsgained': {
                    'tee': 1,
                    'fairway': -1,
                    'rough': 0,
                    'sand': 0,
                    'recovery': 0,
                    'green': round(Decimal(-0.5), 2)
                }
            }
        }
        self.table.put_item(Item=existing_round_stats)

        existing_round = {
            'PK': 'USER#test_user',
            'SK': 'ROUND#06/18/2023-test_course',
            'date': '06/18/2023',
            'course': 'test_course',
            'holes': self.test_shots
        }
        self.table.put_item(Item=existing_round)

        event = {
            'body': json.dumps({
                'userName': 'test_user',
                'round': '06/18/2023-test_course'
            })
        }
        context = {}

        lambda_handler(event, context)
        profile = self.table.get_item(
            Key={
                'PK': 'USER#test_user',
                'SK': 'PROFILE#test_user'
            }
        )
        stats = profile.get('Item').get('stats')
        shots_stats = stats.get('shots')
        shotsgained_stats = stats.get('shotsgained')
        self.assertEqual(shots_stats.get('tee'), 4)
        self.assertEqual(shots_stats.get('fairway'), 2)
        self.assertEqual(shots_stats.get('rough'), 1)
        self.assertEqual(shots_stats.get('sand'), 1)
        self.assertEqual(shots_stats.get('recovery'), 1)
        self.assertEqual(shots_stats.get('green'), 6)
        self.assertEqual(shotsgained_stats.get('tee'), Decimal('-0.29'))
        self.assertEqual(shotsgained_stats.get('fairway'), Decimal('-0.77'))
        self.assertEqual(shotsgained_stats.get('rough'), Decimal('0.45'))
        self.assertEqual(shotsgained_stats.get('sand'), Decimal('0.04'))
        self.assertEqual(shotsgained_stats.get('recovery'), Decimal('-0.17'))
        self.assertEqual(shotsgained_stats.get('green'), Decimal('-0.61'))


if __name__ == '__main__':
    unittest.main()
