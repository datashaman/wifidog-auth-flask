import os
import tempfile
import six
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, BASE_DIR)

from auth import create_app
from auth.models import db, users, Role
from flask_security.utils import encrypt_password
from lxml import etree

with open(BASE_DIR + '/tests/tests.db', 'rb') as local_db:
    content = local_db.read()

class TestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        fd, self.filename = tempfile.mkstemp()
        os.write(fd, content)
        os.close(fd)

        config = {
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + self.filename,
        }

        self.app = create_app(config)
        self.client = self.app.test_client()

    def tearDown(self):
        os.unlink(self.filename)

    def get_html(self, response):
        data = response.get_data()
        parser = etree.HTMLParser()
        return etree.parse(six.StringIO(str(data)), parser)

    def assertOk(self, url):
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        return self.get_html(response)

    def assertRegex(self, *args, **kwargs):
        if six.PY3:
            return super(TestCase, self).assertRegex(*args, **kwargs)
        else:
            return self.assertRegexpMatches(*args, **kwargs)

    def assertTitle(self, html, title):
        self.assertRegex(html.find('//title').text, r'^%s -' % title)

    def urlencode(self, value):
        if six.PY3:
            import urllib.parse
            return urllib.parse.urlencode(value)
        else:
            import urllib
            return urllib.urlencode(value)

    def assertRedirect(self, url, location='http://localhost/'):
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        self.assertEqual(location, response.headers['Location'])

    def assertRedirectPost(self, url, data={}, location='http://localhost/'):
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(location, response.headers['Location'])

    def assertForbidden(self, url):
        response = self.client.get(url, follow_redirects=True)
        html = self.get_html(response)
        li = html.find('//ul[@class="flashes"]/li[@class="error"]')
        self.assertEqual('You do not have permission to view this resource.', li.text)

    def assertForbiddenPost(self, url, data={}):
        response = self.client.post(url, data=data, follow_redirects=True)
        html = self.get_html(response)
        li = html.find('//ul[@class="flashes"]/li[@class="error"]')
        self.assertEqual('You do not have permission to view this resource.', li.text)

    def assertLogin(self, url):
        location = 'http://localhost/login'
        if url != '/':
            location += '?' + self.urlencode({'next': url})
        self.assertRedirect(url, location)

    def assertLoginPost(self, url, data={}):
        location = 'http://localhost/login'
        if url != '/':
            location += '?' + self.urlencode({'next': url})
        self.assertRedirectPost(url, data, location)

    def create_user(self, email, password, role, network_id=None, gateway_id=None):
        with self.app.test_request_context():
            user = users.create_user(email=email, password=encrypt_password(password))

            user.network_id = network_id
            user.gateway_id = gateway_id

            role = Role.query.filter_by(name=role).first_or_404()
            user.roles.append(role)

            db.session.commit()

    def login(self, email, password):
        return self.client.post('/login', data=dict(email=email, password=password))

    def logout(self):
        return self.client.get('/logout')
