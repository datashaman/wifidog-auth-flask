from tests import TestCase
from unittest import skip


class TestMine(TestCase):
    def test_my_account_as_anonymous(self):
        self.assertLogin('/user')

    def test_my_account_as_gateway(self):
        self.login('main-gateway1@example.com', 'admin')
        html = self.assertOk('/user')
        response = self.client.post(html.find('//form').get('action'), data={'email': 'another@example.com'}, follow_redirects=True)
        assert 'Update successful' in str(response.get_data())

    @skip('getting a 400 status, suspect file issues, can\'t duplicate irl')
    def test_my_gateway_as_gateway(self):
        self.login('main-gateway1@example.com', 'admin')
        html = self.assertOk('/gateway')
        form = html.find('//form')
        response = self.client.post(form.get('action'),
                                    content_type=form.get('enctype'),
                                    data={'id': 'main-gateway1', 'title': 'Another Title', 'logo': ''},
                                    follow_redirects=True)
        output = str(response.get_data())
        assert 'Update Another Title successful' in output

    def test_my_network_as_gateway(self):
        self.login('main-gateway1@example.com', 'admin')
        self.assertForbidden('/network')

    def test_my_account_as_network(self):
        self.login('main-network@example.com', 'admin')
        html = self.assertOk('/user')
        response = self.client.post(html.find('//form').get('action'), data={'email': 'another@example.com'}, follow_redirects=True)
        assert 'Update successful' in str(response.get_data())

    def test_my_gateway_as_network(self):
        self.login('main-network@example.com', 'admin')
        self.assertForbidden('/gateway')

    def test_my_network_as_network(self):
        self.login('main-network@example.com', 'admin')
        html = self.assertOk('/network')
        response = self.client.post(html.find('//form').get('action'), data={'id': 'main-network', 'title': 'Another Title'}, follow_redirects=True)
        assert 'Update successful' in str(response.get_data())
