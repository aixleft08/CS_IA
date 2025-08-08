from flask import Flask
import unittest

class BasicTests(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_home(self):
        response = self.client.get('/')
        self.assertEqual(response.data, b'Hello, Flask!')

if __name__ == '__main__':
    unittest.main()