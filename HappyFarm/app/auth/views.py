# -*- coding:utf-8 -*-
import os
from flask import render_template, redirect, flash, session, url_for, current_app, request
from .. import db
from .forms import LoginForm, RegistrationForm, ChangePasswordForm
from flask.ext.login import login_user, logout_user, login_required
from ..models import User
from . import auth
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import StringIO
from datetime import datetime

def generate_verification_code(len=4):
# 注意： 这里我们生成的是0-9A-Za-z的列表，当然你也可以指定这个list，这里很灵活
# 比如： code_list = ['P','y','t','h','o','n','T','a','b'] # PythonTab的字母
	code_list = [] 
	for i in range(10): # 0-9数字
		code_list.append(str(i))
	for i in range(65, 91): # 对应从“A”到“Z”的ASCII码
		code_list.append(chr(i))
	for i in range(97, 123): #对应从“a”到“z”的ASCII码
		code_list.append(chr(i))
	myslice = random.sample(code_list, len) # 从list中随机获取6个元素，作为一个片断返回
	code = ''.join(myslice) # list to string
	return code

#随机字母
def rndChar():
	return chr(random.randint(65, 90))


#随机颜色1:
def rndColor():
	return(random.randint(64, 255),random.randint(64, 255),random.randint(64, 255))

#随机颜色2:
def rndColor2():
	return(random.randint(32, 127),random.randint(32, 127),random.randint(32, 127))

#240x60:
width = 60*4
height = 60
image = Image.new('RGB',(width,height),(255,255,255))
#创建Font对象
font = ImageFont.truetype('/home/su/Library/Fonts/arial.ttf',36)
#创建Draw对象:
draw = ImageDraw.Draw(image)
#填充每个像素:
for x in range(width):
	for y in range(height):
		draw.point((x,y),fill=rndColor())
#输出文字
for t in range(4):
	draw.text((60 * t + 10, 10), rndChar(), font=font, fill=rndColor2())

#模糊:
image = image.filter(ImageFilter.BLUR)
image.save('/home/su/HappyFarm/app/static/image/code/code.jpg','jpeg');

@auth.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(email=form.email.data, phonenum=form.phonenum.data, password=form.password.data, username=form.username.data)
		db.session.add(user)
		db.session.commit()
		#send_email(user.email, 'Confirm Your Account',
#'auth/email/confirm', user=user)
		flash('you have successfully register.')
		return redirect(url_for('.login'))
	return render_template('auth/register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		email = form.email.data
		if email:
			user = User.query.filter_by(email=form.email.data).first()
		else:
			user = User.query.filter_by(phonenum=form.phonenum.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			user.loginip = request.remote_addr
			user.last_seen = datetime.utcnow()
			db.session.add(user)
			return redirect(url_for('main.index'))
		flash('Invalid username or password.')
	return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You have been logout.')
	return redirect(url_for('.login'))

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
	form = ChangePasswordForm()
	if form.validate_on_submit():
		if current_user.verify_password(form.old_password.data):
			current_user.password = form.password.data
			db.session.add(current_user)
			flash('Your password has been updated.')
			return redirect(url_for('.login'))
		else:
			flash('Invalid password.')
	return render_template('auth/change_password.html', form=form)

