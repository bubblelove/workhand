# -*- coding:utf-8 -*-
from ..models import User
from flask.ext.wtf import Form
from wtforms.validators import Required, Email, Regexp, EqualTo, Length
from wtforms import StringField, SubmitField, PasswordField, BooleanField, IntegerField
from wtforms import ValidationError


class RegistrationForm(Form):
	email = StringField(u'邮箱', validators=[Required(), Email(), Length(1,64)])
	phonenum = StringField(u'手机号', validators=[Required()])
	username = StringField(u'用户名', validators=[Required()])
	password = PasswordField(u'密码', validators=[Required(), EqualTo('password2', message='password must to be matched.')])
	password2 = PasswordField(u'确认密码', validators=[Required()])	
	submit = SubmitField(u'注册')

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('Email already registered.')

	def validate_phonenum(self, field):
		if User.query.filter_by(phonenum=field.data).first():
			raise ValidationError('phonenum already registered.')

class LoginForm(Form):
	email = StringField(u'邮箱', validators=[Required(), Email(), Length(1,64)])
	phonenum = IntegerField(u'手机号', validators=[Required()])
	password = PasswordField(u'密码', validators=[Required()])
	remember_me = BooleanField(u'保持登录')
	verification_code = StringField(u'验证码', validators=[Required(), Length(4, 4, message=u'填写4位验证码')])	
	submit = SubmitField(u'登录')

class ChangePasswordForm(Form):
	old_password = PasswordField(u'旧密码', validators=[Required()])
	password = PasswordField(u'新密码', validators=[Required(), EqualTo('password2', message=u'两次输入不一致')])
	password2 = PasswordField(u'再输一次', validators=[Required()])
	submit = SubmitField(u'提交')
