from .. import db, app
from .dbhandler import Movie, Category, MovieCategoryScores, MoviePersonScores, Person
from sqlalchemy.sql import func
import requests
import json
from itertools import islice

tmdb_key = 'db254eee52d0c8fbc70d51368cd24644'

def add_movie(id):
    respons = requests.get('http://api.themoviedb.org/3/movie/' + str(id) + '?api_key=' + tmdb_key)
    if respons.status_code != 200:
        return None
    movie = json.loads(respons.text)
    genres = movie['genres']
    genres.append({'id': 0, 'name': 'Movie'})
    m = Movie(id = movie['id'], name = movie['original_title'])
    for genre in genres:
        cate = Category.query.filter_by(id=genre['id']).first()
        if cate is None:
            cate = add_category(genre['id'], genre['name'])
        a = MovieCategoryScores(score=700, votes=0)
        a.movie = m
        a.category = cate
        cate.movies.append(a)
        db.session.add(a)
    
    respons = requests.get('http://api.themoviedb.org/3/movie/' + str(id) + '/credits?api_key=' + tmdb_key)
    if respons.status_code != 200:
        return None
    mcredits = json.loads(respons.text)
    for actor in islice(mcredits['cast'], 10):
        a = MoviePersonScores(score=700)
        p = get_person(actor['id'])
        a.movie = m
        a.person = p
        p.movies.append(a)
        db.session.add(a)
    db.session.add(m)
    db.session.commit()

def add_category(id, name):
    new = Category(id = id, name = name)
    db.session.add(new)
    db.session.commit()
    return new

def add_person(id):
    respons = requests.get('http://api.themoviedb.org/3/person/' + str(id) + '?api_key=' + tmdb_key)
    if respons.status_code != 200:
        return None
    person = json.loads(respons.text)
    p = Person(id = person['id'], name = person['name'], job=person['known_for_department'], score = 700)
    db.session.add(p)
    db.session.commit()
    return p



def get_person(id):
    p = Person.query.filter_by(id=id).first()
    if p:
        return p
    return add_person(id)

def get_movie(id):
    m = Movie.query.filter_by(id=id).first()
    return m

def get_random_movie():
    m = Movie.query.order_by(func.random()).first()
    return m

def get_category_score(movie_id, category_id):
    m = MovieCategoryScores.query.filter_by(movie_id=movie_id, category_id=category_id).first()
    return m

def get_movie_categories(movie_id):
    movies = MovieCategoryScores.query.filter_by(movie_id=movie_id).all()
    return movies


def vote_for(win, lose):
    winner = MovieCategoryScores.query.filter_by(movie_id = win, category_id = 0).first()
    loser = MovieCategoryScores.query.filter_by(movie_id = lose, category_id = 0).first()
    probW = 1/(1 + (10**((loser.score - winner.score)/400)))
    probL = 1-probW
    print(f'Probability Winner: {probW}, Probability Loser: {probL}')
    winner.score = winner.score + (32*(1 - probW))
    loser.score = loser.score + (32*(0 - probL))
    winner.votes +=1
    loser.votes += 1
    db.session.commit()