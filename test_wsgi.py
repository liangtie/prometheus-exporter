import unittest
from flask import Flask
from wsgi import app, COUNTER_MAP

# FILE: test_wsgi.py


class TestWSGI(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_data_buried_point_success(self):
        response = self.app.post('/data_buried_point', json={'name': 'test_counter', 'doc': 'Test counter documentation'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('msg', response.json)
        self.assertEqual(response.json['msg'], 'ok')
        self.assertIn('test_counter', COUNTER_MAP)

    def test_data_buried_point_success_two(self):
        response = self.app.post('/data_buried_point', json={'name': 'test_counter_two', 'doc': 'Test counter documentation'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('msg', response.json)
        self.assertEqual(response.json['msg'], 'ok')
        self.assertIn('test_counter_two', COUNTER_MAP)        

    def test_data_buried_point_invalid_request(self):
        response = self.app.post('/data_buried_point', json={'invalid_key': 'value'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('description', response.json)
        self.assertEqual(response.json['description'], 'Invalid value.')

if __name__ == '__main__':
    unittest.main()