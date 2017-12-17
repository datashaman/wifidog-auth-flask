from tests import TestCase


class TestSite(TestCase):
    def test_home_redirects_to_login_as_anonymous(self):
        self.assertLogin('/')

    def test_login(self):
        html = self.assertOk('/login')
        self.assertTitle(html, 'Login')

        response = self.login('main-gateway1@example.com', 'admin123')

        self.assertEqual(302, response.status_code)
        self.assertEqual('http://localhost/vouchers', response.headers['Location'])

