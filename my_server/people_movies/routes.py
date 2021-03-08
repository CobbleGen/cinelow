from flask_login import current_user
from my_server import app
from my_server.database import dbhandler as dbh, pers_movie_dbf as pmf
from flask import Blueprint, request, render_template, abort
import requests
import json
from itertools import islice


people_movies = Blueprint('people_movies', __name__)

tmdb_key = 'db254eee52d0c8fbc70d51368cd24644'


@app.route('/m/<movie_id>')
def moviePage(movie_id = None):
    if movie_id == None:
        abort(404)
    respons = requests.get('http://api.themoviedb.org/3/movie/' + movie_id + '?api_key=' + tmdb_key)
    if respons.status_code != 200:
        abort(404)
    pmf.add_movie(movie_id)
    movie_data = json.loads(respons.text)
    categories = pmf.get_movie_categories_with_score(movie_id)
    people = pmf.get_movie_people(movie_id)
    respons = requests.get('https://api.themoviedb.org/3/movie/' + movie_id + '/recommendations?api_key=' + tmdb_key + '&language=en-US&page=1')
    if respons.status_code != 200:
        return None
    recomendations = json.loads(respons.text)['results'][0:10]
    seen = 0
    if current_user.is_authenticated:
        seen = pmf.get_seen_movie(movie_id, current_user.id)
    return render_template('movie.html', movie = movie_data, categories = categories, people = people, recomendations = recomendations, seen = seen)
    

@app.route('/p/<person_id>')
def personPage(person_id = None):
    if person_id == None:
        abort(404)
    respons = requests.get('http://api.themoviedb.org/3/person/' + person_id + '?api_key=' + tmdb_key)
    if respons.status_code != 200:
        abort(404)
    person_data = json.loads(respons.text)
    return render_template('person.html', person = person_data)


@app.route('/compare')
def compare():
    return render_template('compare.html')

@app.route('/toplist/<ctype>/<tid>')
@app.route('/toplist/')
def toplist(ctype='category', tid='0'):
    return render_template('toplist.html', ctype=ctype, tid=tid)

#-------------------------------------------------#
#----------- START OF AJAX REQUESTS --------------#
#-------------------------------------------------#

@app.route('/_getmovies')
def getMovs():
    m1, m2 = pmf.get_random_related_movies(current_user)
    common_cats = pmf.get_common_categories(m1.id, m2.id)
    common_peps = pmf.get_common_people(m1.id, m2.id)
    movies = {
        'm1' : m1.serialize,
        'm2' : m2.serialize,
        'common_categories' : common_cats,
        'common_people'     : common_peps
    }
    return movies

@app.route('/_get_top_list')
def getTopList():
    data_id = int(request.args['data_id'])
    max_amount = int(request.args['amount'])
    movies = []
    category = ""
    if request.args['type'] == 'person':
        movies = pmf.get_top_movies_by_person(data_id)
        category = pmf.get_person(data_id).name
    elif request.args['type'] == 'category':
        movies = pmf.get_top_movies_by_category(data_id)
        category = pmf.get_category(data_id).name
    elif request.args['type'] == 'recommended':
        movies = pmf.get_user_recommendations(data_id, max_amount)
        return {'category': 'rec', 'movies': movies}
    elif request.args['type'] == 'trending':
        respons = requests.get('https://api.themoviedb.org/3/trending/movie/week?api_key=db254eee52d0c8fbc70d51368cd24644')
        if respons.status_code != 200:
            abort(404)
        movies = json.loads(respons.text)['results']
        return {'category': 'rec', 'movies': movies}
    elif request.args['type'] == 'popular':
        respons = requests.get('https://api.themoviedb.org/3/movie/popular?api_key=db254eee52d0c8fbc70d51368cd24644&language=en-US&page=1')
        if respons.status_code != 200:
            abort(404)
        movies = json.loads(respons.text)['results']
        return {'category': 'rec', 'movies': movies}
    movie_list = []
    movie_ids = []
    for movie in islice(movies, max_amount):
        if movie[0].movie_id in movie_ids:
            continue
        movie_ids.append(movie[0].movie_id)
        minfo = movie[0].movie.serialize
        movie_list.append((minfo, movie[0].score, movie[1], movie[0].votes))
    return {'category': category, 'movies': movie_list}

@app.route('/_vote_for_movie', methods=['GET', 'POST'])
def voteMovie():
    wid = request.form['winning_id']
    lid = request.form['losing_id']
    if current_user.is_authenticated:
        pmf.vote_for(wid, lid, current_user.id)
    else:
        pmf.vote_for(wid, lid)
    return 'Success'

@app.route('/_seen_movie', methods=['GET', 'POST'])
def seenMovie():
    mid = request.form['movie_id']
    seen = request.form['seen_value']
    if current_user.is_authenticated:
        pmf.seen_movie(mid, current_user.id, seen)
    return 'Success'
