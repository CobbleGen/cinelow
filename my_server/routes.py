from my_server import app, dbhandler
from my_server.dbhandler import db
from flask import request, url_for, flash, redirect, session, render_template, abort
from .forms import SignupForm, LoginForm, UpdateAccountForm
from flask_login import login_user, current_user, logout_user, login_required
import requests
import json
import bcrypt

tmdb_key = 'db254eee52d0c8fbc70d51368cd24644'

@app.route('/')
def start():
    return render_template('index.html')

@app.route('/m/<movie_id>')
def moviePage(movie_id = None):
    if movie_id == None:
        abort(404)
    respons = requests.get('http://api.themoviedb.org/3/movie/' + movie_id + '?api_key=' + tmdb_key)
    if respons.status_code != 200:
        abort(404)
    movie_data = json.loads(respons.text)
    respons = requests.get('http://api.themoviedb.org/3/movie/' + movie_id + '/credits?api_key=' + tmdb_key)
    credits = respons.json()
    cast = credits['cast']
    directors = []
    writers = []
    for person in credits['crew']:
        if person['job'] == 'Director':
            directors.append(person)
        elif person['job'] == 'Screenplay':
            writers.append(person)
    
    return render_template('movie.html', movie = movie_data, directors = directors, writers = writers, cast = cast)
    

@app.route('/p/<person_id>')
def personPage(person_id = None):
    if person_id == None:
        abort(404)
    respons = requests.get('http://api.themoviedb.org/3/person/' + person_id + '?api_key=' + tmdb_key)
    if respons.status_code != 200:
        abort(404)
    person_data = json.loads(respons.text)
    respons = requests.get('http://api.themoviedb.org/3/person/' + person_id + '/movie_credits?api_key=' + tmdb_key)
    credits = respons.json()
    movies = credits['cast']
    movies.sort(key=lambda x: x.get('popularity'), reverse=True)
    return render_template('person.html', person = person_data, movies = movies)

@app.route('/login', methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('start'))
    form = LoginForm()
    if form.validate_on_submit():
        user = dbhandler.getUserByEmail(form.email.data)
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
        if dbhandler.usernameExists(form.username.data):
            flash(f'User {form.username.data} already exists.', 'warning')
        elif dbhandler.emailExists(form.email.data):
            flash(f'That email is already being used.', 'warning')
        else:
            hashed_pw = bcrypt.hashpw(form.password.data.encode('UTF-8'), bcrypt.gensalt())
            dbhandler.createUser(form.username.data, form.email.data, hashed_pw)
            flash(f'Account created for {form.username.data}!', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/u/<uname>')
def user(uname=None):
    if uname == None:
        abort(404)
    user = dbhandler.getUserByUname(uname)
    return render_template('user.html', user = user)

@app.route('/account', methods=["POST", "GET"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            dbhandler.save_picture(form.picture.data)
        if form.new_password.data:
            hashed_pw = bcrypt.hashpw(form.new_password.data.encode('UTF-8'), bcrypt.gensalt())
            current_user.password = hashed_pw
        current_user.username = form.username.data
        current_user.email = form.email.data
        dbhandler.commitDB()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', form = form)