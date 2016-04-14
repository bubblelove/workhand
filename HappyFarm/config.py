# -*- coding:utf-8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@localhost/happyfarms'
	WHOOSH_BASE = os.path.join(basedir, 'search.db')
	MAX_SEARCH_RESULTS = 50
	MAIL_SERVER = 'smtp.googlemail.com'
	MAIL_PORT = 587
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	FLASKY_MAIL_SUBJECT_PERFIX = '[Flasky]'
	FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'
	FLASKY_ADMIN = '805898349@qq.com'
	FLASKY_POSTS_PER_PAGE = 20
	FLASKY_COMMENTS_PER_PAGE = 20
	MAX_SEARCH_RESULTS = 50
	DEBUG = True

	@staticmethod
	def init_app(app):
		pass

config = { 'default': Config}
