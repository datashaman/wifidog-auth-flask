from app.utils import args_get
from flask.ext.wtf import Form
from wtforms import HiddenField, PasswordField, TextField, validators

from .models import Network

from wtforms.ext.sqlalchemy.orm import model_form
NetworkForm = model_form(Network, base_class=Form, exclude_pk=False, field_args = {
    'title': {
        'validators': [ validators.Length(min=5, max=20) ],
    },
})
