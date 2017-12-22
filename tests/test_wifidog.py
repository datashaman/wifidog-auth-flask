from six.moves.urllib import parse

from auth import constants
from auth.models import Voucher
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

    def test_login(self):
        with self.app.test_request_context():
            voucher_code = 'main-1-1'

            data = {
                'gw_address': '192.168.2.1',
                'gw_port': 2060,
                'gw_id': 'main-gateway1',
                'ip': '192.168.2.254',
                'mac': '11:22:33:44:55:66',
                'url': 'http://www.google.com/',
            }

            url = '/wifidog/login/?%s' % parse.urlencode(data)

            pq = self.assertOk(url)
            url = pq('form')[0].get('action')

            data.update({
                'voucher_code': voucher_code,
            })

            response = self.client.post(url, data=data)
            voucher = Voucher.query.filter(Voucher.code == data['voucher_code']).first()

            self.assertEqual(302, response.status_code)
            self.assertEqual('http://%s:%d/wifidog/auth?token=%s'
                             % (data['gw_address'],
                                data['gw_port'],
                                voucher.token),
                             response.headers['Location'])

            data = {
                'stage': 'login',
                'mac': '11:22:33:44:55:66',
                'token': voucher.token,
                'incoming': 0,
                'outgoing': 0,
                'gw_id': 'main-gateway1',
            }
            url = '/wifidog/auth/?%s' % parse.urlencode(data)
            response = self.client.get(url)

            self.assertEqual(200, response.status_code)
            self.assertEqual('Auth: %d\nMessages: None\n'
                             % constants.AUTH_ALLOWED,
                             response.get_data().decode())

            data['stage'] = 'counters'
            data['incoming'] = 100
            data['outgoing'] = 200

            url = '/wifidog/auth/?%s' % parse.urlencode(data)
            response = self.client.get(url)

            self.assertEqual(200, response.status_code)
            self.assertEqual('Auth: %d\nMessages: \n'
                             % constants.AUTH_ALLOWED,
                             response.get_data().decode())

            voucher = Voucher.query.filter(Voucher.code == voucher_code).first()

            self.assertEqual(data['incoming'], voucher.incoming)
            self.assertEqual(data['outgoing'], voucher.outgoing)

    def test_portal_without_gw_id(self):
        response = self.client.get('/wifidog/portal/')
        self.assertEqual(404, response.status_code)

    def test_portal_with_invalid_gw_id(self):
        response = self.client.get('/wifidog/portal/?gw_id=foobar')
        self.assertEqual(404, response.status_code)

    def test_portal_with_valid_gw(self):
        response = self.client.get('/wifidog/portal/?gw_id=main-gateway1')
        self.assertEqual(200, response.status_code)
