from tests import TestCase

from auth.models import Country
from wtforms.ext.sqlalchemy.fields import identity_key


class TestThing(TestCase):
    def test_it(self):
        with self.app.test_request_context():
            c = Country.query.first()
            actual = identity_key(instance=c)
            print(actual)
            self.assertEqual((type(c), (c.id,)), actual)
