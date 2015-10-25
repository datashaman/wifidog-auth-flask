#!/usr/bin/env python

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

    def test_vouchers_index(self):
        self.login('main-gateway1@example.com', 'admin')

        response = self.client.get('/vouchers', follow_redirects=True)
        self.assertEquals(200, response.status_code)

        html = self.get_html(response)
        vouchers = html.find('//vouchers')

        assert vouchers is not None

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
