from tests import TestCase


class TestMine(TestCase):
    def test_my_account_as_anonymous(self):
        self.assertLogin('/user')

    def test_my_account_as_gateway(self):
        self.login('main-gateway1@example.com', 'admin')
        html = self.assertOk('/user')
        response = self.client.post(html.find('//form').get('action'), data={'email': 'another@example.com'}, follow_redirects=True)
        assert 'Update successful' in str(response.get_data())

    def test_my_gateway_as_gateway(self):
        self.login('main-gateway1@example.com', 'admin')
        html = self.assertOk('/gateway')
        response = self.client.post(html.find('//form').get('action'), data={'id': 'main-gateway1', 'title': 'Another Title'}, follow_redirects=True)
        assert 'Update Main Gateway #1 successful' in str(response.get_data())

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
