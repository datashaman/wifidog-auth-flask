from tests import TestCase

from auth.models import Country, Currency
from sqlalchemy.orm.base import object_mapper
from wtforms.ext.sqlalchemy.fields import identity_key


class TestThing(TestCase):
    def test_country(self):
        with self.app.test_request_context():
            c = Country.query.first()
            mapper = object_mapper(c)
            pk = mapper.primary_key_from_instance(c)
            self.assertEqual(pk, (c.id,))
            ik = mapper.identity_key_from_primary_key(pk)
            self.assertEqual((type(c), (c.id,)), ik)
