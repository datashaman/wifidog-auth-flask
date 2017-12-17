from tests import TestCase


class TestViews(TestCase):
    def test_read_or_404(self):
        self.login('main-gateway1@example.com', 'admin123')

        response = self.client.get('/api/networks/unknown-network')
        self.assertEqual(404, response.status_code)
