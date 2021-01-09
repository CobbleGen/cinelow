from my_server import app
from my_server.database import dbhandler as dbh, user_dbf as uf
from flask import Blueprint, request, url_for, flash, redirect, session, render_template, abort
from my_server.forms import SignupForm, LoginForm, UpdateAccountForm
from flask_login import login_user, current_user, logout_user, login_required
import bcrypt

users = Blueprint('users', __name__)

@app.route('/login', methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('start'))
    form = LoginForm()
    if form.validate_on_submit():
        user = uf.getUserByEmail(form.email.data)
        if user == None:
            flash(f'No user could be found with that email.', 'warning')
        elif bcrypt.checkpw(form.password.data.encode('UTF-8'), user.password):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('start'))
        else:
            flash('Wrong password or email address.', 'warning')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('start'))

@app.route('/register', methods=["POST", "GET"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('start'))
    form = SignupForm()
    if form.validate_on_submit():
        if uf.getUserByUname(form.username.data):
            flash(f'User {form.username.data} already exists.', 'warning')
        elif uf.getUserByEmail(form.email.data):
            flash(f'That email is already being used.', 'warning')
        else:
            hashed_pw = bcrypt.hashpw(form.password.data.encode('UTF-8'), bcrypt.gensalt())
            uf.createUser(form.username.data, form.email.data, hashed_pw)
            flash(f'Account created for {form.username.data}!', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/u/<uname>')
def user(uname=None):
    if uname == None:
        abort(404)
    user = uf.getUserByUname(uname)
    return render_template('user.html', user = user)

@app.route('/account', methods=["POST", "GET"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            uf.save_picture(form.picture.data)
        if form.new_password.data:
            hashed_pw = bcrypt.hashpw(form.new_password.data.encode('UTF-8'), bcrypt.gensalt())
            current_user.password = hashed_pw
        current_user.username = form.username.data
        current_user.email = form.email.data
        dbh.commitDB()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', form = form)