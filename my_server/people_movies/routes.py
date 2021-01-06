from my_server import app
from my_server import dbhandler as dbh
from flask import Blueprint, request, url_for, redirect, render_template, abort
import requests
import json

people_movies = Blueprint('people_movies', __name__)

tmdb_key = 'db254eee52d0c8fbc70d51368cd24644'


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