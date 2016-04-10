# -*- coding:utf-8 -*-
from . import db
from datetime import datetime
from app.exceptions import ValidationError
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin
from . import login_manager
from flask import current_app
from markdown import markdown
import bleach
import flask.ext.whooshalchemy as whooshalchemy
from flask import Flask, url_for
import hashlib
from flask import request

app = Flask(__name__)

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class Follow(db.Model):
	__tablename__ = 'follows'
	follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
	followed_id = db.Column(db.Integer, db.ForeignKey('stores.id'), primary_key=True)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Chat(db.Model):
	__tablename__ = 'chats'
	id = db.Column(db.Integer, primary_key=True)
	body1 = db.Column(db.Text)
	body2 = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	message_id = db.Column(db.Integer, db.ForeignKey('users.id'),
primary_key=True)
	contact_id = db.Column(db.Integer, db.ForeignKey('users.id'),
primary_key=True)

class Order(db.Model):
	__tablename__ = 'orders'
	id = db.Column(db.Integer, primary_key=True)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow)
	mounts = db.Column(db.String(3), default='1')
	laterpay = db.Column(db.Boolean, default=False)
	complete = db.Column(db.Boolean, default=False)
	seller_id = db.Column(db.Integer, db.ForeignKey('stores.id'))
	buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	
	def to_json(self):
		json_post = {
			'url': url_for('api.get_order', id = self.id, _external = True),
			'timestamp': self.timestamp,
			'mounts': self.mounts,
			#'seller': self.seller_id,
			'seller': self.seller.name,
			'buyer': self.buyer.username,

		}
		return json_post	

	@staticmethod
	def from_json(json_post):  #JSON格式转化成模型实例
		mounts = json_post.get('mounts')
		if mounts is None or mounts == '':
			raise ValidationError(u'请确定数量')
		return Order(mounts = mounts)

class User(UserMixin, db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(64), unique=True)
	phonenum = db.Column(db.String(64), unique=True)
	username = db.Column(db.String(64), index=True)
	password_hash = db.Column(db.String(128))
	realname = db.Column(db.String(64))
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
	location = db.Column(db.String(128))
	bussiness = db.Column(db.Boolean, default=False)
	about_me = db.Column(db.Text())
	sex = db.Column(db.String(64), default='male')
	birthday = db.Column(db.DateTime)
	member_since = db.Column(db.DateTime, default=datetime.utcnow)
	last_seen = db.Column(db.DateTime, default=datetime.utcnow)
	loginip = db.Column(db.String(64))
	shippingadd = db.Column(db.String(128))
	head = db.Column(db.String(128))
	avatar_hash = db.Column(db.String(32))
	stores = db.relationship('Store', backref='host', lazy='dynamic')
	comments = db.relationship('Comment', backref='author', lazy='dynamic')
	bbs = db.relationship('BB', backref='writer', lazy='dynamic')
	feedback = db.relationship('Feedback', backref='adviser', lazy='dynamic')
	myorder = db.relationship('Order', backref='buyer', lazy='dynamic')
	followed = db.relationship('Follow', foreign_keys=[Follow.follower_id], backref=db.backref('follower', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')
	message = db.relationship('Chat', foreign_keys=[Chat.contact_id], backref=db.backref('contact', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')
	contact = db.relationship('Chat', foreign_keys=[Chat.message_id], backref=db.backref('message', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')


	def __init__(self, **kwargs):
		super(User, self).__init__(**kwargs)
		if self.role is None:
			if self.email == current_app.config['FLASKY_ADMIN']:
				self.role = Role.query.filter_by(permissions=0xff).first()
			if self.role is None:
				self.role = Role.query.filter_by(default=True).first()
		if self.email is not None and self.avatar_hash is None:
			self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

	def change_email(self, token):
		self.email = new_email
		self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
		db.session.add(self)
		return True
	
	def can(self, permissions):
		return self.role is not None and \
			(self.role.permissions & permissions) == permissions
	
	def is_administrator(self):
		return self.can(Permission.ADMINISTER)

	def follow(self, store):
		if not self.is_following(store):
			f = Follow(follower=self, followed=store)
			db.session.add(f)

	def unfollow(self, store):
		f = self.followed.filter_by(followed_id=store.id).first()
		if f:
			db.session.delete(f)

	def is_following(self, store):
		return self.followed.filter_by(followed_id=store.id).first() is not None

	def gravatar(self, size=100, default='identicon', rating='g'):
		if request.is_secure:
			url = 'https://secure.gravatar.com/avatar'
		else:
			url = 'http://www.gravatar.com/avatar'
		hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
		return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
url=url, hash=hash, size=size, default=default, rating=rating)
	
	def to_url(self):
		if self.head:
			return self.string(self.head)

	def string(self, s):
        	return r'<img src="' + s +r'">'
	
	@property
	def password(self):  #define password.setter's password函数
		raise AttributeError('password is not a readable attribute')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)
		
	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	@staticmethod
	def generate_fake(count=100):
		from sqlalchemy.exc import IntegrityError
		from random import seed
		import forgery_py

		seed()
		for i in range(count):
			u = User(email=forgery_py.internet.email_address(),
username=forgery_py.internet.user_name(True),
password=forgery_py.lorem_ipsum.word(),
realname=forgery_py.name.full_name(),
loaction=forgery_py.address.city(),
about_me=forgery_py.lorem_ipsum.sentence(),
member_since=forgery_py.date.date(True))
			db.session.add(u)
			try:
				db.session.commit()
			except IntegrityError:
				db.session.rollback()

class AnonymousUser(AnonymousUserMixin):
	def can(self, permission):
		return False
	def is_administer(self):
		return False
login_manager.anonymous_user = AnonymousUser  #匿名用户，酱紫程序不用检查用户是否登录
	

class Permission:
	FOLLOW = 0x01
	COMMENT = 0x02
	WRITE_ARTICLES = 0x04
	MODERATE_COMMENTS = 0x08
	ADMINISTER = 0x80

class Role(db.Model):
	__tablename__ = 'roles'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)  #角色名
	default = db.Column(db.Boolean, default=False, index=True)
	permissions = db.Column(db.Integer)
	users = db.relationship('User', backref='role', lazy='dynamic')
	
	@staticmethod
	def insert_roles():
		roles = {
			'User': (Permission.FOLLOW |
					Permission.COMMENT |
					Permission.WRITE_ARTICLES, True),
			'Moderator': (Permission.FOLLOW |
						Permission.COMMENT |
						Permission.WRITE_ARTICLES |
						Permission.MODERATE_COMMENTS, False),
			'Administrator': (0xff, False)
		}
		for r in roles:
			role  = Role.query.filter_by(name=r).first()
			if role is None:
				role = Role(name=r)
			role.permissions = roles[r][0]
			role.default = roles[r][1]
			db.session.add(role)  
		db.session.commit()

#class Discount(db.Model):
#	__tablename__ == 'discounts'
#	id = db.Column(db.Integer, primary_key=True)

class Store(db.Model):
	__tablename__ = 'stores'
	__searchable__ = ['name']
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64))
	address = db.Column(db.String(64))
	pic = db.Column(db.String(64))
	price = db.Column(db.String(32))
	introduce = db.Column(db.Text())
	comments = db.relationship('Comment', backref='store', lazy='dynamic')
	bulid_since = db.Column(db.DateTime, default=datetime.utcnow, index=True)
	host_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	orders = db.relationship('Order', backref='seller', lazy='dynamic')
	followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
backref=db.backref('followed', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')

	def is_followed_by(self, user):
		return self.followers.filter_by(follower_id=user.id).first() is not None


whooshalchemy.whoosh_index(app, Store)

class Comment(db.Model):
	__tablename__ = 'comments'
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	disabled = db.Column(db.Boolean, default=False)
	count = db.Column(db.Boolean, default=False)
	author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))

class Feedback(db.Model):
	__tablename__ = 'feedbacks'
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.Text)
	adviser_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class BB(db.Model):
	__tablename__ = 'bbs'
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	writer_id = db.Column(db.Integer, db.ForeignKey('users.id'))

