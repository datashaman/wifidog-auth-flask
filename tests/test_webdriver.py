import os
import sys
import new
import unittest
import time
import json
from selenium import webdriver
from sauceclient import SauceClient

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, BASE_DIR)

USERNAME = os.environ.get('SAUCE_USERNAME')
ACCESS_KEY = os.environ.get('SAUCE_ACCESS_KEY')

sauce = SauceClient(USERNAME, ACCESS_KEY)

FLASK_EMAIL = 'super-admin@example.com'
FLASK_PASSWORD = 'admin'

with open(BASE_DIR + '/tests/config.json') as config:
    browserMatrix = json.load(config)

def on_platforms(platforms):
    def decorator(base_class):
        module = sys.modules[base_class.__module__].__dict__
        for i, platform in enumerate(platforms):
            d = dict(base_class.__dict__)
            d['desired_capabilities'] = platform
            d['user'] = 'user%d' % i
            name = '%s_%s' % (base_class.__name__, i + 1)
            module[name] = new.classobj(name, (base_class,), d)
    return decorator

@on_platforms(browserMatrix['browser'])
class SauceSampleTest(unittest.TestCase):
    def setUp(self):
        self.desired_capabilities['name'] = str(self)
        self.desired_capabilities['username'] = USERNAME
        self.desired_capabilities['access-key'] = ACCESS_KEY

        if os.environ.get('TRAVIS_BUILD_NUMBER'):
            self.desired_capabilities[
                'build'] = os.environ.get('TRAVIS_BUILD_NUMBER')
            self.desired_capabilities[
                'tunnel-identifier'] = os.environ.get('TRAVIS_JOB_NUMBER')

        self.driver = webdriver.Remote(
            desired_capabilities=self.desired_capabilities,
            command_executor='http://localhost:4445/wd/hub'
        )

        self.driver.implicitly_wait(30)

    def login(self):
        self.driver.get('http://localhost:8080/login')
        name = self.driver.find_element_by_name('email')
        name.send_keys(FLASK_EMAIL)
        pw = self.driver.find_element_by_name('password')
        pw.send_keys(FLASK_PASSWORD)
        button = self.driver.find_element_by_id('submit')
        button.click()
        print 'logged in'

    def test_login(self):
        # login
        self.login()

        # login check
        message = self.driver.find_element_by_css_selector('.flashes').text
        assert 'You were logged in' in message

    def tearDown(self):
        try:
            if sys.exc_info() == (None, None, None):
                sauce.jobs.update_job(self.driver.session_id, passed=True, public=True)
            else:
                sauce.jobs.update_job(self.driver.session_id, passed=False, public=True)
        finally:
            self.driver.quit()

if __name__ == '__main__':
    unittest.main()
