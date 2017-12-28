from tests import TestCase

from auth.models import Country, Currency
from wtforms.ext.sqlalchemy.fields import identity_key


class TestThing(TestCase):
    def test_country(self):
        with self.app.test_request_context():
            c = Country.query.first()
            actual = identity_key(instance=c)
            print(actual)
            self.assertEqual((type(c), (c.id,)), actual)

    def test_currency(self):
        with self.app.test_request_context():
            c = Currency.query.first()
            actual = identity_key(instance=c)
            print(actual)
            self.assertEqual((type(c), (c.id,)), actual)
