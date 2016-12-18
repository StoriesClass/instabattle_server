import unittest
import json
from base64 import b64encode
from flask import url_for
from app import create_app, db
from app.helpers import generate_fake_user
from app.models import User


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @staticmethod
    def get_api_headers(username, password):
        return {
            'Authorization': 'Basic ' + b64encode((
                                                      username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_404(self):
        response = self.client.get(
            '/wrong/url',
            headers=self.get_api_headers('email', 'password'))
        self.assertTrue(response.status_code == 404)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['error'] == 'not found')

    def test_no_auth(self):
        response = self.client.get(
            url_for('api.battles_list'),
            content_type='application/json')
        self.assertTrue(response.status_code == 200)

    def test_bad_auth(self):
        u = generate_fake_user(email="test@me.me", password="123")
        db.session.add(u)
        db.session.commit()

        # authenticate with bad password
        response = self.client.get(
            url_for('api.battles_list'),
            headers=self.get_api_headers('test@me.me', '456'))
        self.assertTrue(response.status_code == 401)

    def test_token_auth(self):
        u = generate_fake_user(email="test@me.me", password="123")
        db.session.add(u)
        db.session.commit()

        # issue a request with a bad token
        response = self.client.get(
            url_for('api.battles_list'),
            headers=self.get_api_headers('bad-token', ''))
        self.assertTrue(response.status_code == 401)

        # get a token
        response = self.client.get(
            url_for('api.get_token'),
            headers=self.get_api_headers('test@me.me', '123'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIsNotNone(json_response.get('token'))
        token = json_response['token']

        # issue a request with the token
        response = self.client.get(
            url_for('api.battles_list'),
            headers=self.get_api_headers(token, ''))
        self.assertTrue(response.status_code == 200)

    def test_anonymous(self):
        response = self.client.get(
            url_for('api.battles_list'),
            headers=self.get_api_headers('', ''))
        self.assertTrue(response.status_code == 200)

    def test_users(self):
        # add two users
        u1 = generate_fake_user(username="one", email="one@me.me", password="123")
        u2 = generate_fake_user(username="two", email="two@me.me", password="456")
        db.session.add_all([u1, u2])
        db.session.commit()

        # get users
        response = self.client.get(
            url_for('api.user', username=u1.username),
            headers=self.get_api_headers('one@me.me', '123'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['id'] == u1.id)
        response = self.client.get(
            url_for('api.user', username=u2.username),
            headers=self.get_api_headers('two@me.me', '456'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['id'] == u2.id)
