from tests import TestCase


class TestNetworks(TestCase):
    def test_networks_index_as_anonymous(self):
        self.assertLogin('/networks')

    def test_networks_index_as_gateway(self):
        self.login('main-gateway1@example.com', 'admin')
        self.assertRedirect('/networks')

    def test_networks_index_as_network(self):
        self.login('main-network@example.com', 'admin')
        self.assertRedirect('/networks')

    def test_networks_index_as_super(self):
        self.login('super-admin@example.com', 'admin')

        html = self.assertOk('/networks')
        networks = html.findall('//table[@id="networks"]/tbody/tr')

        self.assertEqual(2, len(networks))

        self.assertEqual('main-network', networks[0].get('data-id'))

    def test_networks_new_as_anonymous(self):
        self.assertLogin('/networks/new')

    def test_networks_new_as_gateway(self):
        self.login('main-gateway1@example.com', 'admin')
        self.assertForbidden('/networks/new')

    def test_networks_new_as_network(self):
        self.login('main-network@example.com', 'admin')
        self.assertForbidden('/networks/new')

    def test_networks_new_as_super(self):
        self.login('super-admin@example.com', 'admin')

        response = self.client.get('/networks/new')
        self.assertEqual(200, response.status_code)
