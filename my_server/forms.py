from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from my_server import dbhandler
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from wtforms_validators import NotEqualTo
from flask_login import current_user
import email_validator
import bcrypt

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log in')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Picture', validators=[FileAllowed(['jpg', 'png'])])
    current_password = PasswordField('Current Password', validators=[Optional()])
    new_password = PasswordField('New Password', validators=[Optional(), Length(min=5, max=20), NotEqualTo('current_password')])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            if dbhandler.usernameExists(username.data):
                raise ValidationError('That username is taken.')

    def validate_email(self, email):
        if email.data != current_user.email:
            if dbhandler.emailExists(email.data):
                raise ValidationError('That email is already being used.')

    def validate_current_password(self, current_password):
        if not bcrypt.checkpw(self.current_password.data.encode('UTF-8'), current_user.password):
            raise ValidationError('Incorrect password.')