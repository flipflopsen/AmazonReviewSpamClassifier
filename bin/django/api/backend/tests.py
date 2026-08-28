from django.test import Client, TestCase
from rest_framework.response import Response
import json

# Create your tests here.


class PostEndpointTest(TestCase):
    def test_post_endpoint(self):
        client = Client()

        data_ham = {'review_text': 'The product is ok but not really good.'}
        headers = {'Content-Type': 'application/json'}
        response = client.post('/sendreview/', data=data_ham, content_type='application/json')

        json_data = json.loads(response.content)
        result = json_data['result']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result, 0)
        print('Successfully detected Ham!')

        data_spam = {'review_text': 'Best prooduct ever! You should really buy it ony my store page right now.'}
        headers = {'Content-Type': 'application/json'}
        response = client.post('/sendreview/', data=data_spam, content_type='application/json')

        json_data = json.loads(response.content)
        result = json_data['result']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result, 1)
        print('Successfully detected Spam!')
