#!/usr/bin/env python

import json
import os
import tempfile
import unittest

from app import create_app, init_db
from app.models import db, users, Role
from flask import current_app
from flask.ext.security.utils import encrypt_password
from lxml import etree
from manage import create_roles, create_user, create_network, create_gateway
from StringIO import StringIO

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

with open(BASE_DIR + '/data/tests.db', 'r') as tests_db:
    content = tests_db.read()

class TestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        self.app = create_app()

        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False

        self.fd, self.filename = tempfile.mkstemp()
        os.write(self.fd, content)

        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + self.filename
        init_db(self.app)

        self.client = self.app.test_client()

    def tearDown(self):
        self.logout()

        os.close(self.fd)
        os.unlink(self.filename)

    def get_html(self, response):
        data = response.get_data()
        parser = etree.HTMLParser()
        return etree.parse(StringIO(response.get_data()), parser)

    def assertTitle(self, html, title):
        self.assertRegexpMatches(html.find('//title').text, r'^%s -' % title)

    def create_user(self, email, password, role, network_id=None, gateway_id=None):
        with self.app.test_request_context():
            user = users.create_user(email=email, password=encrypt_password(password))

            user.network_id = network_id
            user.gateway_id = gateway_id

            role = Role.query.filter_by(name=role).first_or_404()
            user.roles.append(role)

            db.session.commit()

    def login(self, email, password, follow_redirects=False):
        return self.client.post('/login', data=dict(email=email, password=password), follow_redirects=follow_redirects)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    def test_home_redirects_to_login(self):
        response = self.client.get('/')
        self.assertEquals(302, response.status_code)
        self.assertEquals('http://localhost/login', response.headers['Location'])

    def test_login(self):
        response = self.client.get('/login')
        self.assertEquals(200, response.status_code)

        html = self.get_html(response)
        self.assertTitle(html, 'Login')

        response = self.login('main-gateway1@example.com', 'admin')

        self.assertEquals(302, response.status_code)
        self.assertEquals('http://localhost/vouchers', response.headers['Location'])

    def test_api_networks_index_as_gateway(self):
        self.login('main-gateway1@example.com', 'admin')

        response = self.client.get('/api/networks')
        self.assertEquals(200, response.status_code)

        networks = json.loads(response.data)
        self.assertEquals(1, len(networks))

        self.assertEquals('main-network', networks[0]['id'])

    def test_api_networks_index_as_network(self):
        self.login('main-network@example.com', 'admin')

        response = self.client.get('/api/networks')
        self.assertEquals(200, response.status_code)

        networks = json.loads(response.data)
        self.assertEquals(1, len(networks))

        self.assertEquals('main-network', networks[0]['id'])

    def test_api_networks_index_as_super(self):
        self.login('super-admin@example.com', 'admin')

        response = self.client.get('/api/networks')
        self.assertEquals(200, response.status_code)

        networks = json.loads(response.data)
        self.assertEquals(2, len(networks))

        self.assertEquals('main-network', networks[0]['id'])
        self.assertEquals('other-network', networks[1]['id'])

    def test_api_gateways_index_as_gateway(self):
        self.login('main-gateway1@example.com', 'admin')

        response = self.client.get('/api/gateways', follow_redirects=True)
        self.assertEquals(200, response.status_code)

        gateways = json.loads(response.data)
        self.assertEquals(1, len(gateways))

        self.assertEquals('main-gateway1', gateways[0]['id'])

    def test_api_gateways_index_as_network(self):
        self.login('main-network@example.com', 'admin')

        response = self.client.get('/api/gateways')
        self.assertEquals(200, response.status_code)

        gateways = json.loads(response.data)
        self.assertEquals(2, len(gateways))

        self.assertEquals('main-gateway1', gateways[0]['id'])
        self.assertEquals('main-gateway2', gateways[1]['id'])

    def test_api_gateways_index_as_super(self):
        self.login('super-admin@example.com', 'admin')

        response = self.client.get('/api/gateways')
        self.assertEquals(200, response.status_code)

        gateways = json.loads(response.data)
        self.assertEquals(4, len(gateways))

        self.assertEquals('main-gateway1', gateways[0]['id'])
        self.assertEquals('main-gateway2', gateways[1]['id'])
        self.assertEquals('other-gateway1', gateways[2]['id'])
        self.assertEquals('other-gateway2', gateways[3]['id'])

    def test_api_users_index_as_gateway(self):
        self.login('main-gateway1@example.com', 'admin')

        response = self.client.get('/api/users')
        self.assertEquals(200, response.status_code)

        users = json.loads(response.data)
        self.assertEquals(1, len(users))

        self.assertEquals('main-gateway1@example.com', users[0]['email'])

    def test_api_users_index_as_network(self):
        self.login('main-network@example.com', 'admin')

        response = self.client.get('/api/users?sort={"email":false}')
        self.assertEquals(200, response.status_code)

        users = json.loads(response.data)
        self.assertEquals(3, len(users))

        self.assertEquals('main-gateway1@example.com', users[0]['email'])
        self.assertEquals('main-gateway2@example.com', users[1]['email'])
        self.assertEquals('main-network@example.com', users[2]['email'])

    def test_api_users_index_as_super(self):
        self.login('super-admin@example.com', 'admin')

        response = self.client.get('/api/users')
        self.assertEquals(200, response.status_code)

        users = json.loads(response.data)
        self.assertEquals(7, len(users))

    def test_api_vouchers_index_as_gateway(self):
        self.login('main-gateway1@example.com', 'admin')

        response = self.client.get('/api/vouchers')
        self.assertEquals(200, response.status_code)

        vouchers = json.loads(response.data)
        self.assertEquals(2, len(vouchers))

        self.assertEquals('main-1-1', vouchers[0]['$id'])
        self.assertEquals('main-1-2', vouchers[1]['$id'])

    def test_api_vouchers_index_as_network(self):
        self.login('main-network@example.com', 'admin')

        response = self.client.get('/api/vouchers?sort={"$id":false}')
        self.assertEquals(200, response.status_code)

        vouchers = json.loads(response.data)
        self.assertEquals(4, len(vouchers))

    def test_api_users_index_as_super(self):
        self.login('super-admin@example.com', 'admin')

        response = self.client.get('/api/users')
        self.assertEquals(200, response.status_code)

        users = json.loads(response.data)
        self.assertEquals(7, len(users))

    def test_voucher_new_as_gateway(self):
        self.login('main-gateway1@example.com', 'admin')

        response = self.client.get('/voucher', follow_redirects=True)
        self.assertEquals(200, response.status_code)

        html = self.get_html(response)
        options = html.findall('//select[@id="gateway_id"]/option')

        self.assertEquals(1, len(options))
        self.assertEquals('main-gateway1', options[0].get('value'))

    def test_voucher_new_as_network(self):
        self.login('main-network@example.com', 'admin')

        response = self.client.get('/voucher', follow_redirects=True)
        self.assertEquals(200, response.status_code)

        html = self.get_html(response)
        options = html.findall('//select[@id="gateway_id"]/option')

        self.assertEquals(2, len(options))

        self.assertEquals('main-gateway1', options[0].get('value'))
        self.assertEquals('main-gateway2', options[1].get('value'))

    def test_voucher_new_as_super(self):
        self.login('super-admin@example.com', 'admin')

        response = self.client.get('/voucher', follow_redirects=True)
        self.assertEquals(200, response.status_code)

        html = self.get_html(response)
        options = html.findall('//select[@id="gateway_id"]/option')

        self.assertEquals(4, len(options))

        self.assertEquals('main-gateway1', options[0].get('value'))
        self.assertEquals('main-gateway2', options[1].get('value'))
        self.assertEquals('other-gateway1', options[2].get('value'))
        self.assertEquals('other-gateway2', options[3].get('value'))

if __name__ == '__main__':
    unittest.main()
