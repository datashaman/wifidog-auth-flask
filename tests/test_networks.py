from tests import TestCase


class TestNetworks(TestCase):
    def test_networks_index_as_anonymous(self):
        self.assertLogin('/networks')

    def test_networks_index_as_gateway(self):
        self.login('main-gateway1@example.com', 'admin123')
        self.assertRedirect('/networks')

    def test_networks_index_as_network(self):
        self.login('main-network@example.com', 'admin123')
        self.assertRedirect('/networks')

    def test_networks_index_as_super(self):
        self.login('super-admin@example.com', 'admin123')

        html = self.assertOk('/networks')
        networks = html.findall('//table[@id="networks"]/tbody/tr')

        self.assertEqual(2, len(networks))

        self.assertEqual('main-network', networks[0].get('data-id'))

    def test_networks_new_as_anonymous(self):
        self.assertLogin('/networks/new')

    def test_networks_new_as_gateway(self):
        self.login('main-gateway1@example.com', 'admin123')
        self.assertForbidden('/networks/new')

    def test_networks_new_as_network(self):
        self.login('main-network@example.com', 'admin123')
        self.assertForbidden('/networks/new')

    def test_networks_new_as_super(self):
        self.login('super-admin@example.com', 'admin123')

        response = self.client.get('/networks/new')
        self.assertEqual(200, response.status_code)

    def test_networks_store_as_anonymous(self):
        self.assertLoginPost('/networks/new', data={'id': 'network', 'title': 'Network'})

    def test_networks_store_as_gateway(self):
        self.login('main-gateway1@example.com', 'admin123')
        self.assertForbiddenPost('/networks/new', data={'id': 'network', 'title': 'Network'})

    def test_networks_store_as_network(self):
        self.login('main-network@example.com', 'admin123')
        self.assertForbiddenPost('/networks/new', data={'id': 'network', 'title': 'Network'})

    def test_networks_store_as_super(self):
        self.login('super-admin@example.com', 'admin123')
        response = self.client.post('/networks/new', data={'id': 'network', 'title': 'Network'}, follow_redirects=True)
        self.assertEqual(200, response.status_code)

    def test_networks_edit_as_anonymous(self):
        self.assertLogin('/networks/main-network')

    def test_networks_edit_as_gateway(self):
        self.login('main-gateway1@example.com', 'admin123')
        self.assertForbidden('/networks/main-network')

    def test_networks_edit_as_network(self):
        self.login('main-network@example.com', 'admin123')
        self.assertForbidden('/networks/main-network')

    def test_networks_edit_as_super(self):
        self.login('super-admin@example.com', 'admin123')
        response = self.client.get('/networks/main-network')
        self.assertEqual(200, response.status_code)

    def test_networks_update_as_anonymous(self):
        self.assertLoginPost('/networks/main-network', {'id': 'network', 'title': 'Network'})

    def test_networks_update_as_gateway(self):
        self.login('main-gateway1@example.com', 'admin123')
        self.assertForbiddenPost('/networks/main-network')

    def test_networks_update_as_network(self):
        self.login('main-network@example.com', 'admin123')
        self.assertForbiddenPost('/networks/main-network')

    def test_networks_update_as_super(self):
        self.login('super-admin@example.com', 'admin123')
        response = self.client.post('/networks/main-network', data={'id': 'network', 'title': 'Network'}, follow_redirects=True)
        self.assertEqual(200, response.status_code)
