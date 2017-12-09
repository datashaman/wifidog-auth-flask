from flask import url_for
from tests import TestCase


class TestVouchers(TestCase):
    def test_voucher_new_as_anonymous(self):
        with self.app.test_request_context():
            self.assertLogin(url_for('.voucher_new'))

    def test_voucher_new_as_gateway(self):
        with self.app.test_request_context():
            self.login('main-gateway1@example.com', 'admin')

            response = self.client.get(url_for('.voucher_new'), follow_redirects=True)
            self.assertEqual(200, response.status_code)

            html = self.get_html(response)
            options = html.findall('//select[@id="gateway_id"]/option')

            self.assertEqual(1, len(options))
            self.assertEqual('main-gateway1', options[0].get('value'))

    def test_voucher_new_as_network(self):
        with self.app.test_request_context():
            self.login('main-network@example.com', 'admin')

            response = self.client.get(url_for('.voucher_new'), follow_redirects=True)
            self.assertEqual(200, response.status_code)

            html = self.get_html(response)
            options = html.findall('//select[@id="gateway_id"]/option')

            self.assertEqual(2, len(options))

            self.assertEqual('main-gateway1', options[0].get('value'))
            self.assertEqual('main-gateway2', options[1].get('value'))

    def test_voucher_new_as_super(self):
        with self.app.test_request_context():
            self.login('super-admin@example.com', 'admin')

            response = self.client.get(url_for('.voucher_new'), follow_redirects=True)
            self.assertEqual(200, response.status_code)

            html = self.get_html(response)
            options = html.findall('//select[@id="gateway_id"]/option')

            self.assertEqual(4, len(options))

            self.assertEqual('main-gateway1', options[0].get('value'))
            self.assertEqual('main-gateway2', options[1].get('value'))
            self.assertEqual('other-gateway1', options[2].get('value'))
            self.assertEqual('other-gateway2', options[3].get('value'))

    def test_voucher_index_as_anonymous(self):
        self.assertLogin('/vouchers')

    def test_voucher_index_as_gateway(self):
        self.login('main-gateway1@example.com', 'admin')

        html = self.assertOk('/vouchers')
        vouchers = html.findall('//table[@id="vouchers"]/tbody/tr')

        self.assertEqual(2, len(vouchers))
        self.assertEqual('main-1-2', vouchers[0].get('data-code'))
        self.assertEqual('main-1-1', vouchers[1].get('data-code'))

    def test_voucher_index_as_network(self):
        self.login('main-network@example.com', 'admin')

        html = self.assertOk('/vouchers')
        vouchers = html.findall('//table[@id="vouchers"]/tbody/tr')

        self.assertEqual(4, len(vouchers))
        self.assertEqual('main-2-2', vouchers[0].get('data-code'))
        self.assertEqual('main-2-1', vouchers[1].get('data-code'))
        self.assertEqual('main-1-2', vouchers[2].get('data-code'))
        self.assertEqual('main-1-1', vouchers[3].get('data-code'))

    def test_voucher_index_as_super(self):
        self.login('super-admin@example.com', 'admin')

        html = self.assertOk('/vouchers')
        vouchers = html.findall('//table[@id="vouchers"]/tbody/tr')

        self.assertEqual(8, len(vouchers))
        self.assertEqual('other-2-2', vouchers[0].get('data-code'))
        self.assertEqual('other-2-1', vouchers[1].get('data-code'))
        self.assertEqual('other-1-2', vouchers[2].get('data-code'))
        self.assertEqual('other-1-1', vouchers[3].get('data-code'))
        self.assertEqual('main-2-2', vouchers[4].get('data-code'))
        self.assertEqual('main-2-1', vouchers[5].get('data-code'))
        self.assertEqual('main-1-2', vouchers[6].get('data-code'))
        self.assertEqual('main-1-1', vouchers[7].get('data-code'))

    def test_voucher_archive_as_gateway(self):
        self.login('main-gateway1@example.com', 'admin')

        html = self.assertOk('/vouchers')
        code = html.find('//table[@id="vouchers"]//td[@class="code"]').text
        button = html.find('//table[@id="vouchers"]//a[@title="archive"]')

        html = self.assertOk(button.get('href'))
        form = html.find('//div[@class="content"]/form')

        response = self.client.post(form.get('action'), follow_redirects=True)
        assert '%s archive successful' % code in str(response.get_data())

    def test_voucher_archive_as_network(self):
        self.login('main-network@example.com', 'admin')

        html = self.assertOk('/vouchers')
        code = html.find('//table[@id="vouchers"]//td[@class="code"]').text
        button = html.find('//table[@id="vouchers"]//a[@title="archive"]')

        html = self.assertOk(button.get('href'))
        form = html.find('//div[@class="content"]/form')

        response = self.client.post(form.get('action'), follow_redirects=True)
        assert '%s archive successful' % code in str(response.get_data())

    def test_voucher_archive_as_super(self):
        self.login('super-admin@example.com', 'admin')

        html = self.assertOk('/vouchers')
        code = html.find('//table[@id="vouchers"]//td[@class="code"]').text
        button = html.find('//table[@id="vouchers"]//a[@title="archive"]')

        html = self.assertOk(button.get('href'))
        form = html.find('//div[@class="content"]/form')

        response = self.client.post(form.get('action'), follow_redirects=True)
        assert '%s archive successful' % code in str(response.get_data())
