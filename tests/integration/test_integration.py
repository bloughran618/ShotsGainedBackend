import unittest
from unittest.mock import MagicMock
from python.create_user.create_user import lambda_handler


class TestLambdaHandler(unittest.TestCase):

    def setUp(self):
        self.event = {
            'body': '{"userName": "test_user", "name": "Test User"}'
        }
        self.context = MagicMock()

    def test_lambda_handler_user_already_exists(self):
        # Test case where user already exists in the database
        self.event['body'] = '{"userName": "existing_user", "name": "Existing User"}'
        response = lambda_handler(self.event, self.context)
        self.assertEqual(response['statusCode'], 409)
        self.assertIn('Username already exists', response['body'])


if __name__ == '__main__':
    unittest.main()
