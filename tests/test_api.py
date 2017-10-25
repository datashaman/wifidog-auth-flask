import json

from tests import TestCase

class TestApi(TestCase):
    def test_api_networks_index_as_anonymous(self):
        response = self.client.get('/api/networks')
        self.assertEqual(403, response.status_code)

    def test_api_networks_index_as_gateway(self):
        self.login('main-gateway1@example.com', 'admin')

        response = self.client.get('/api/networks')
        self.assertEqual(200, response.status_code)

        networks = json.loads(response.get_data(True))
        self.assertEqual(1, len(networks))

        self.assertEqual('main-network', networks[0]['id'])

    def test_api_networks_index_as_network(self):
        self.login('main-network@example.com', 'admin')

        response = self.client.get('/api/networks')
        self.assertEqual(200, response.status_code)

        networks = json.loads(response.get_data(True))
        self.assertEqual(1, len(networks))

        self.assertEqual('main-network', networks[0]['id'])

    def test_api_networks_index_as_super(self):
        self.login('super-admin@example.com', 'admin')

        response = self.client.get('/api/networks')
        self.assertEqual(200, response.status_code)

        networks = json.loads(response.get_data(True))
        self.assertEqual(2, len(networks))

        self.assertEqual('main-network', networks[0]['id'])
        self.assertEqual('other-network', networks[1]['id'])

    def test_api_gateways_index_as_anonymous(self):
        response = self.client.get('/api/gateways')
        self.assertEqual(403, response.status_code)

    def test_api_gateways_index_as_gateway(self):
        self.login('main-gateway1@example.com', 'admin')

        response = self.client.get('/api/gateways', follow_redirects=True)
        self.assertEqual(200, response.status_code)

        gateways = json.loads(response.get_data(True))
        self.assertEqual(1, len(gateways))

        self.assertEqual('main-gateway1', gateways[0]['id'])

    def test_api_gateways_index_as_network(self):
        self.login('main-network@example.com', 'admin')

        response = self.client.get('/api/gateways')
        self.assertEqual(200, response.status_code)

        gateways = json.loads(response.get_data(True))
        self.assertEqual(2, len(gateways))

        self.assertEqual('main-gateway1', gateways[0]['id'])
        self.assertEqual('main-gateway2', gateways[1]['id'])

    def test_api_gateways_index_as_super(self):
        self.login('super-admin@example.com', 'admin')

        response = self.client.get('/api/gateways')
        self.assertEqual(200, response.status_code)

        gateways = json.loads(response.get_data(True))
        self.assertEqual(4, len(gateways))

        self.assertEqual('main-gateway1', gateways[0]['id'])
        self.assertEqual('main-gateway2', gateways[1]['id'])
        self.assertEqual('other-gateway1', gateways[2]['id'])
        self.assertEqual('other-gateway2', gateways[3]['id'])

    def test_api_users_index_as_anonymous(self):
        response = self.client.get('/api/users')
        self.assertEqual(403, response.status_code)

    def test_api_users_index_as_gateway(self):
        self.login('main-gateway1@example.com', 'admin')

        response = self.client.get('/api/users')
        self.assertEqual(200, response.status_code)

        users = json.loads(response.get_data(True))
        self.assertEqual(1, len(users))

        self.assertEqual('main-gateway1@example.com', users[0]['email'])

    def test_api_users_index_as_network(self):
        self.login('main-network@example.com', 'admin')

        response = self.client.get('/api/users?sort={"email":false}')
        self.assertEqual(200, response.status_code)

        users = json.loads(response.get_data(True))
        self.assertEqual(3, len(users))

        self.assertEqual('main-gateway1@example.com', users[0]['email'])
        self.assertEqual('main-gateway2@example.com', users[1]['email'])
        self.assertEqual('main-network@example.com', users[2]['email'])

    def test_api_users_index_as_super(self):
        self.login('super-admin@example.com', 'admin')

        response = self.client.get('/api/users')
        self.assertEqual(200, response.status_code)

        users = json.loads(response.get_data(True))
        self.assertEqual(7, len(users))

    def test_api_vouchers_index_as_anonymous(self):
        response = self.client.get('/api/vouchers')
        self.assertEqual(403, response.status_code)

    def test_api_vouchers_index_as_gateway(self):
        self.login('main-gateway1@example.com', 'admin')

        response = self.client.get('/api/vouchers')
        self.assertEqual(200, response.status_code)

        vouchers = json.loads(response.get_data(True))
        self.assertEqual(2, len(vouchers))

        self.assertEqual('main-1-2', vouchers[0]['code'])
        self.assertEqual('main-1-1', vouchers[1]['code'])

    def test_api_vouchers_index_as_network(self):
        self.login('main-network@example.com', 'admin')

        response = self.client.get('/api/vouchers?sort={"code":false}')
        self.assertEqual(200, response.status_code)

        vouchers = json.loads(response.get_data(True))
        self.assertEqual(4, len(vouchers))

    def test_api_users_index_as_super(self):
        self.login('super-admin@example.com', 'admin')

        response = self.client.get('/api/users')
        self.assertEqual(200, response.status_code)

        users = json.loads(response.get_data(True))
        self.assertEqual(7, len(users))
