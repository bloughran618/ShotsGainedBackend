import json
import unittest

import sys
sys.path.append('../../python/shots_gained_common/layer/python/lib/python3.9/site-packages')

from python.calc_shots_gained.calc_shots_gained import lambda_handler


class TestLambdaHandler(unittest.TestCase):

    def setUp(self):
        self.context = {}
        self.malformed_event_string = "Malformed event body, does not look like # " \
                                      "{'from': {'distance': 450, 'type': 'TEE'}, " \
                                      "'to': {'distance': 115, 'type': 'FAIRWAY'}}"

    def test_lambda_handler_missing_from(self):
        event = {
            'body': json.dumps({
                'to': {'distance': 115, 'type': 'FAIRWAY'}
            })
        }

        response = lambda_handler(event, self.context)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['error'], self.malformed_event_string)
        self.assertEqual(json.loads(response['body'])['input'], json.loads(event['body']))

    def test_lambda_handler_missing_to(self):
        event = {
            'body': json.dumps({
                'from': {'distance': 450, 'type': 'TEE'},
            })
        }

        response = lambda_handler(event, self.context)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['error'], self.malformed_event_string)
        self.assertEqual(json.loads(response['body'])['input'], json.loads(event['body']))

    def test_lambda_handler_missing_from_distance(self):
        event = {
            'body': json.dumps({
                'from': {'type': 'TEE'},
                'to': {'distance': 115, 'type': 'FAIRWAY'}
            })
        }

        response = lambda_handler(event, self.context)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['error'], self.malformed_event_string)
        self.assertEqual(json.loads(response['body'])['input'], json.loads(event['body']))

    def test_lambda_handler_missing_from_type(self):
        event = {
            'body': json.dumps({
                'from': {'distance': 450},
                'to': {'distance': 115, 'type': 'FAIRWAY'}
            })
        }

        response = lambda_handler(event, self.context)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['error'], self.malformed_event_string)
        self.assertEqual(json.loads(response['body'])['input'], json.loads(event['body']))

    def test_lambda_handler_successful(self):
        event = {
            'body': json.dumps({
                'from': {'distance': 450, 'type': 'TEE'},
                'to': {'distance': 115, 'type': 'FAIRWAY'}
            })
        }

        response = lambda_handler(event, self.context)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], '{"shots_gained": 0.33}')


if __name__ == '__main__':
    unittest.main()
