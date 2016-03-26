# -*- coding:utf-8 -*-
from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response, g
from flask.ext.login import login_required, current_user
from flask.ext.sqlalchemy import get_debug_queries
from . import main
from .forms import EditProfileForm, AddShippingForm, SettleForm, StoreCommentForm, FeedbackForm, SearchForm
from .. import db
from ..models import Permission, Role, User, Store, Comment, Feedback
from ..decorators import admin_required, permission_required
from datetime import datetime

@main.route('/index', methods=['GET', 'POST'])
def index():
	page = request.args.get('page', 1, type=int)
	pagination = Store.query.order_by(Store.bulid_since.desc()).paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
	stores = pagination.items
	form = SearchForm()
	if form.validate_on_submit():
		return redirect(url_for('main.search_results', query = form.search.data))
	return render_template('index.html', stores=stores, pagination=pagination, form=form)

@main.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
	form = FeedbackForm()
	if form.validate_on_submit():
		feed = Feedback(body=form.body.data, adviser=current_user._get_current_object())
		db.session.add(feed)
		flash(u'提交成功，感谢您的建议于反馈')
		return redirect(url_for('.index'))
	user = current_user
	feeds = Feedback.query.all()
	return render_template('feedback.html', form=form, user=user, feeds=feeds)
	

@main.route('/user/<int:id>')
def user(id):
	user = User.query.get_or_404(id)
	stores = user.stores.order_by(Store.bulid_since.desc())
	if user is None:
		abort(404)
	return render_template('user.html', user=user, stores=stores)

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.realname = form.realname.data
		current_user.sex = form.sex.data
		current_user.birthday = form.birthday.data
		current_user.about_me = form.about_me.data
		db.session.add(current_user)
		flash('Your Profile has been updated.')
		return redirect(url_for('.user', id=current_user.id))
	form.username.data = current_user.username
	form.realname.data = current_user.realname
	form.sex.data = current_user.sex
	form.birthday.data = current_user.birthday
	form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', form=form)

@main.route('/safe')
@login_required
def safe():
	return render_template('safe.html')
	
@main.route('/shipping', methods=['GET', 'POST'])
def shipping():
	form = AddShippingForm()
	if form.validate_on_submit():
		current_user.shippingadd = form.province.data + ' ' + form.city.data + ' ' + form.detailadd.data + ' ' + form.zipcode.data + ' ' + form.phonenum.data + ' ' + form.receiver.data
		db.session.add(current_user)
	return render_template('shipping.html', form=form)

@main.route('/store/<int:id>', methods=['GET', 'POST'])
def store(id):
	store = Store.query.get_or_404(id)
	if store is None:
		abort(404)
	host = store.host
	form = StoreCommentForm()
	comments = Comment.query.filter_by(store_id=store.id).all()
	if form.validate_on_submit():
		comment = Comment(body=form.body.data, author=current_user._get_current_object(), store=store)
		db.session.add(comment)
		return redirect(url_for('main.store', id=store.id))
	return render_template('store.html', store=store, host=host, form=form, comments=comments)

@main.route('/settle', methods=['GET', 'POST'])
@login_required
def settle():
	form = SettleForm()
	if form.validate_on_submit():
		#current_user.stores = [Store(address=form.address.data, introduce=form.introduce.data)]
		store = Store(name=form.name.data,address=form.address.data, price=form.price.data, introduce=form.introduce.data, host=current_user._get_current_object())
		current_user.bussiness = True
		db.session.add(store)
		db.session.add(current_user)
		db.session.commit()
		flash('application pass')
		return redirect(url_for('main.store', id=store.id))
	return render_template('settle.html', form=form)
	

@main.route('/search_results/<query>')
def search_results(query):
	results = Store.query.filter_by(name=query).all()
	return render_template('search_results.html', query=query, results=results)
