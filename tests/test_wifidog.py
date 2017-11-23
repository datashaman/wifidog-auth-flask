from tests import TestCase


class TestWifidog(TestCase):
    def test_login_without_gw_id(self):
        response = self.client.get('/wifidog/login/')
        self.assertEqual(404, response.status_code)

    def test_login_with_invalid_gw_id(self):
        response = self.client.get('/wifidog/login/?gw_id=foobar')
        self.assertEqual(404, response.status_code)

    def test_login_with_valid_gw(self):
        response = self.client.get('/wifidog/login/?gw_id=main-gateway1')
        self.assertEqual(200, response.status_code)

    def test_portal_without_gw_id(self):
        response = self.client.get('/wifidog/portal/')
        self.assertEqual(404, response.status_code)

    def test_portal_with_invalid_gw_id(self):
        response = self.client.get('/wifidog/portal/?gw_id=foobar')
        self.assertEqual(404, response.status_code)

    def test_portal_with_valid_gw(self):
        response = self.client.get('/wifidog/portal/?gw_id=main-gateway1')
        self.assertEqual(200, response.status_code)
