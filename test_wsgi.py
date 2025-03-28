import unittest
from flask import json
from wsgi import app, SOURCE_VISITED_IPS, COUNTER_MAP
from datetime import datetime
class DataBuriedPointTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        SOURCE_VISITED_IPS.clear()
        COUNTER_MAP.clear()

    def test_data_buried_point_first_visit(self):
        response = self.app.post('/data_buried_point', data=json.dumps({
            'name': 'test_name',
            'doc': 'test_doc'
        }), content_type='application/json')

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['msg'], 'ok')
        self.assertFalse(data['visited_before'])

    def test_data_buried_point_repeat_visit(self):
        response = self.app.post('/data_buried_point', data=json.dumps({
            'name': 'test_name',
            'doc': 'test_doc'
        }), content_type='application/json')

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['msg'], 'ok')
        self.assertFalse(data['visited_before'])


        response = self.app.post('/data_buried_point', data=json.dumps({
            'name': 'test_name',
            'doc': 'test_doc'
        }), content_type='application/json')

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['msg'], 'ok')
        self.assertTrue(data['visited_before'])


    def test_data_buried_point_invalid_data(self):
        response = self.app.post('/data_buried_point', data=json.dumps({
            'invalid': 'data'
        }), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('description', data)

if __name__ == '__main__':
    unittest.main()