from flask import url_for
from tests import TestCase


class TestSite(TestCase):
    def test_home_redirects_to_login_as_anonymous(self):
        with self.app.test_request_context():
            self.assertLogin(url_for('auth.home'))

    def test_login(self):
        with self.app.test_request_context():
            pq = self.assertOk('/login')
            self.assertTitle(pq, 'Login')

            response = self.login('main-gateway1@example.com', 'admin123')

            self.assertEqual(302, response.status_code)
            self.assertEqual(url_for('voucher.index', _external=True), response.headers['Location'])
