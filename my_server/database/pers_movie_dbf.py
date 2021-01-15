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
    actors = islice(mcredits['cast'], 10)
    for actor in actors:
        a = MoviePersonScores(score=700)
        p = get_person(actor['id'])
        a.movie = m
        a.person = p
        p.movies.append(a)
        db.session.add(a)
    for person in mcredits['crew']:
            if person['job'] == 'Director':
                if not MoviePersonScores.query.filter_by(movie_id=id, person_id = person['id']).first():
                    a = MoviePersonScores(score=700)
                    p = get_person(person['id'])
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


def delete_movie(id):
    MovieCategoryScores.query.filter_by(movie_id=id).delete()
    MoviePersonScores.query.filter_by(movie_id=id).delete()
    Movie.query.filter_by(id=id).delete()
    db.session.commit()


def get_person(id):
    p = Person.query.filter_by(id=id).first()
    if p:
        return p
    return add_person(id)

def get_category(id):
    c = Category.query.filter_by(id=id).first()
    return c

def get_movie(id):
    m = Movie.query.filter_by(id=id).first()
    return m

def get_random_movie(id = None):
    m = Movie.query.order_by(func.random()).first()
    if id != None:
        if m.id == id:
            return get_random_movie(id)
    return m

def get_top_movies_by_category(category_id):
    m = MovieCategoryScores.query.filter_by(category_id=category_id).order_by(MovieCategoryScores.score.desc()).all()
    return m

def get_top_movies_by_person(person_id):
    m = MoviePersonScores.query.filter_by(person_id=person_id).order_by(MoviePersonScores.score.desc()).all()
    return m

def get_category_score(movie_id, category_id):
    m = MovieCategoryScores.query.filter_by(movie_id=movie_id, category_id=category_id).first()
    return m

def get_movie_categories(movie_id):
    movies = MovieCategoryScores.query.filter_by(movie_id=movie_id).all()
    return movies

def get_common_categories(movie1, movie2):
    categories = MovieCategoryScores.query.with_entities(MovieCategoryScores.category_id).filter(MovieCategoryScores.movie_id.in_([movie1, movie2])).all()
    categories.sort()
    common = []
    for index, category in enumerate(categories):
        if index+1 < len(categories) and categories[index+1] == category:
            common.append(category[0])
    return common

def get_people_score(movie_id, person_id):
    p = MoviePersonScores.query.filter_by(movie_id=movie_id, person_id=person_id).first()
    return p

def get_movie_people(movie_id):
    people = MoviePersonScores.query.filter_by(movie_id=movie_id).all()
    peoplewi = {}
    for person in people:
        peoplewi[person.person_id] = person
    return peoplewi

def get_common_people(movie1, movie2):
    people = MoviePersonScores.query.with_entities(MoviePersonScores.person_id)\
        .filter(MoviePersonScores.movie_id.in_([movie1, movie2])).all()
    people.sort()
    common = []
    for index, person in enumerate(people):
        if index+1 < len(people) and people[index+1] == person:
            common.append(person[0])
    return common


def vote_for(win, lose):
    #Set score for all common categories
    common = get_common_categories(win, lose)
    for category in common:
        winner = MovieCategoryScores.query.filter_by(movie_id = win, category_id = category).first()
        loser = MovieCategoryScores.query.filter_by(movie_id = lose, category_id = category).first()
        probW = 1/(1 + (10**((loser.score - winner.score)/400)))
        probL = 1-probW
        winner.score = winner.score + (32*(1 - probW))
        loser.score = loser.score + (32*(0 - probL))
        winner.votes +=1
        loser.votes += 1
        db.session.commit()
    
    #Set Score for all common people
    common = get_common_people(win, lose)
    for person in common:
        winner = MoviePersonScores.query.filter_by(movie_id = win, person_id = person).first()
        loser = MoviePersonScores.query.filter_by(movie_id = lose, person_id = person).first()
        probW = 1/(1 + (10**((loser.score - winner.score)/400)))
        probL = 1-probW
        winner.score = winner.score + (32*(1 - probW))
        loser.score = loser.score + (32*(0 - probL))
        db.session.commit()

def get_movie_rank_by_person(movie_id):
    query = db.session.query(
    MoviePersonScores,
    func.rank()\
        .over(
            order_by=MoviePersonScores.score
        )\
        .label('rank')
    )
    # now filter
    query = query.filter_by(movie_id=movie_id)
    # Or, just get the first value
    my_movie = query.first()
    return my_movie