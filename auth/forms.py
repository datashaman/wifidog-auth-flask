from __future__ import absolute_import

from auth.models import db, Adjustment
from auth.resources import resource_query
from flask_wtf import FlaskForm
from wtforms import fields as f, validators
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.ext.sqlalchemy.orm import converts, model_form, ModelConverter as BaseModelConverter


def instances(resource):
    def func():
        return resource_query(resource).all()
    return func


class ModelConverter(BaseModelConverter):
    @converts('String', 'Unicode')
    def conv_String(self, field_args, **extra):
        if extra['column'].name == 'logo':
            return f.FileField(**field_args)
        else:
            return BaseModelConverter.conv_String(self, field_args, **extra)

    @converts('auth.models.SqliteDecimal')
    def conv_SqliteDecimal(self, column, field_args, **extra):
        return BaseModelConverter.handle_decimal_types(self, column, field_args, **extra)


model_converter = ModelConverter()

class BroadcastForm(FlaskForm):
    message = f.StringField('Message', [validators.InputRequired()])


class SelectCategoryForm(FlaskForm):
    category = QuerySelectField('Category', query_factory=instances('category'))


class FilterForm(FlaskForm):
    def filter_query(self, query):
        for k, v in self.data.items():
            if v:
                if hasattr(self, 'filter_%s' % k):
                    query = getattr(self, 'filter_%s' % k)(query, k, v)
                else:
                    query = query.filter_by(**{k: v})
        return query
