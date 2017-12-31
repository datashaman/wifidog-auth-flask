from flask import url_for
from tests import TestCase
from unittest import skip


class TestMine(TestCase):
    def test_my_account_as_anonymous(self):
        with self.app.test_request_context():
            self.assertLogin(url_for('user.mine'))

    def test_my_account_as_gateway(self):
        with self.app.test_request_context():
            self.login('main-gateway1@example.com', 'admin123')
            pq = self.assertOk(url_for('user.mine'))
            response = self.client.post(pq('form').attr('action'), data={'email': 'main-gateway1@example.com', 'first_name': 'Another Main', 'locale': 'en', 'timezone': 'UTC'}, follow_redirects=True)
            assert 'Update successful' in str(response.get_data())

    @skip('getting a 400 status, suspect file issues, can\'t duplicate irl')
    def test_my_gateway_as_gateway(self):
        with self.app.test_request_context():
            self.login('main-gateway1@example.com', 'admin123')
            pq = self.assertOk(url_for('gateway.mine'))
            form = pq('form')
            response = self.client.post(form.attr('action'),
                                        content_type=form.attr('enctype'),
                                        data={'id': 'main-gateway1', 'title': 'Another Title', 'logo': ''},
                                        follow_redirects=True)
            output = str(response.get_data())
            assert 'Update Another Title successful' in output

    def test_my_network_as_gateway(self):
        with self.app.test_request_context():
            self.login('main-gateway1@example.com', 'admin123')
            self.assertForbidden(url_for('network.mine'))

    def test_my_account_as_network(self):
        with self.app.test_request_context():
            self.login('main-network@example.com', 'admin123')
            pq = self.assertOk(url_for('user.mine'))
            response = self.client.post(pq('form').attr('action'), data={'email': 'main-network@example.com', 'first_name': 'Another Main', 'locale': 'en', 'timezone': 'UTC'}, follow_redirects=True)
            assert 'Update successful' in str(response.get_data())

    def test_my_gateway_as_network(self):
        with self.app.test_request_context():
            self.login('main-network@example.com', 'admin123')
            self.assertForbidden(url_for('gateway.mine'))

    def test_my_network_as_network(self):
        with self.app.test_request_context():
            self.login('main-network@example.com', 'admin123')
            pq = self.assertOk(url_for('network.mine'))
            response = self.client.post(pq('form').attr('action'), data={'id': 'main-network', 'title': 'Another Title'}, follow_redirects=True)
            assert 'Update successful' in str(response.get_data())
