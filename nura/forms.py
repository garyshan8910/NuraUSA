from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from nura.models import AssistUser


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField('Sign In')


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Password Repeat", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = AssistUser.query.filter_by(username=username.data).first()
        print(user)
        if user is not None:
            raise ValidationError('please use different username')

    def validate_email(self, email):
        user = AssistUser.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('please use different email address')


class SoForm(FlaskForm):
    num = StringField("SO Number")
    submit = SubmitField('search')
