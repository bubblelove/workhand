# -*- coding:utf-8 -*-

from ..models import User
from flask.ext.wtf import Form
from wtforms.validators import Required, Email, Regexp, EqualTo, Length
from wtforms import StringField, SubmitField, PasswordField, BooleanField, IntegerField
from wtforms import ValidationError


class RegistrationForm(Form):
	email = StringField('Email', validators=[Required(), Email(), Length(1,64)])
	phonenum = IntegerField('Phonenumber', validators=[Required()])
	password = PasswordField('Password', validators=[Required(), EqualTo('password2', message='password must to be matched.')])
	password2 = PasswordField('confirmed your password.', validators=[Required()])	
	submit = SubmitField('Register')

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('Email already registered.')

	def validate_phonenum(self, field):
		if User.query.filter_by(phonenum=field.data).first():
			raise ValidationError('phonenum already registered.')

class LoginForm(Form):
	email = StringField('Email', validators=[Required(), Email(), Length(1,64)])
	phonenum = IntegerField('Phonenumber', validators=[Required()])
	password = PasswordField('Password', validators=[Required()])
	remember_me = BooleanField('keep me logged in ')
	#verification_code = StringField(u'验证码', validators=[Required(), Length(4, 4, message=u'填写4位验证码')])	
	submit = SubmitField('Log In')
