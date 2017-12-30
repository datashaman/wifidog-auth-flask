from flask import url_for
from tests import TestCase


class TestNetworks(TestCase):
    def test_networks_index_as_anonymous(self):
        with self.app.test_request_context():
            self.assertLogin(url_for('network.index'))

    def test_networks_index_as_gateway(self):
        with self.app.test_request_context():
            self.login('main-gateway1@example.com', 'admin123')
            self.assertRedirect(url_for('network.index'))

    def test_networks_index_as_network(self):
        with self.app.test_request_context():
            self.login('main-network@example.com', 'admin123')
            self.assertRedirect(url_for('network.index'))

    def test_networks_index_as_super(self):
        with self.app.test_request_context():
            self.login('super-admin@example.com', 'admin123')

            pq = self.assertOk(url_for('network.index'))
            networks = pq('table#networks > tbody > tr')

            self.assertEqual(2, len(networks))

            self.assertEqual('main-network', networks[0].get('data-id'))

    def test_networks_new_as_anonymous(self):
        with self.app.test_request_context():
            self.assertLogin(url_for('network.new'))

    def test_networks_new_as_gateway(self):
        with self.app.test_request_context():
            self.login('main-gateway1@example.com', 'admin123')
            self.assertForbidden(url_for('network.new'))

    def test_networks_new_as_network(self):
        with self.app.test_request_context():
            self.login('main-network@example.com', 'admin123')
            self.assertForbidden(url_for('network.new'))

    def test_networks_new_as_super(self):
        with self.app.test_request_context():
            self.login('super-admin@example.com', 'admin123')

            response = self.client.get(url_for('network.new'))
            self.assertEqual(200, response.status_code)

    def test_networks_store_as_anonymous(self):
        with self.app.test_request_context():
            self.assertLoginPost(url_for('network.new'),
                                 data={'id': 'network', 'title': 'Network'})

    def test_networks_store_as_gateway(self):
        with self.app.test_request_context():
            self.login('main-gateway1@example.com', 'admin123')
            self.assertForbiddenPost(url_for('network.new'),
                                     data={'id': 'network',
                                           'title': 'Network'})

    def test_networks_store_as_network(self):
        with self.app.test_request_context():
            self.login('main-network@example.com', 'admin123')
            self.assertForbiddenPost(url_for('network.new'),
                                     data={'id': 'network',
                                           'title': 'Network'})

    def test_networks_store_as_super(self):
        with self.app.test_request_context():
            self.login('super-admin@example.com', 'admin123')
            response = self.client.post(url_for('network.new'),
                                        data={'id': 'network',
                                              'title': 'Network'},
                                        follow_redirects=True)
            self.assertEqual(200, response.status_code)

    def test_networks_edit_as_anonymous(self):
        with self.app.test_request_context():
            self.assertLogin(url_for('network.edit', id='main-network'))

    def test_networks_edit_as_gateway(self):
        with self.app.test_request_context():
            self.login('main-gateway1@example.com', 'admin123')
            self.assertForbidden(url_for('network.edit', id='main-network'))

    def test_networks_edit_as_network(self):
        with self.app.test_request_context():
            self.login('main-network@example.com', 'admin123')
            self.assertForbidden(url_for('network.edit', id='main-network'))

    def test_networks_edit_as_super(self):
        with self.app.test_request_context():
            self.login('super-admin@example.com', 'admin123')
            response = self.client.get(url_for('network.edit', id='main-network'))
            self.assertEqual(200, response.status_code)

    def test_networks_update_as_anonymous(self):
        with self.app.test_request_context():
            self.assertLoginPost(url_for('network.edit', id='main-network'), {'id': 'network', 'title': 'Network'})

    def test_networks_update_as_gateway(self):
        with self.app.test_request_context():
            self.login('main-gateway1@example.com', 'admin123')
            self.assertForbiddenPost(url_for('network.edit', id='main-network'))

    def test_networks_update_as_network(self):
        with self.app.test_request_context():
            self.login('main-network@example.com', 'admin123')
            self.assertForbiddenPost(url_for('network.edit', id='main-network'))

    def test_networks_update_as_super(self):
        with self.app.test_request_context():
            self.login('super-admin@example.com', 'admin123')
            response = self.client.post(url_for('network.edit', id='main-network'), data={'id': 'network', 'title': 'Network'}, follow_redirects=True)
            self.assertEqual(200, response.status_code)
