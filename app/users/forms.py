from app.utils import args_get
from wtforms import Form, PasswordField, TextField, HiddenField, validators

class LoginForm(Form):
    email = TextField('Email', [ validators.InputRequired() ])
    password = PasswordField('Password', [ validators.InputRequired() ])
    next = HiddenField(default=args_get('next'))

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()

        if user is None:
            raise validators.ValidationError('User does not exist')

