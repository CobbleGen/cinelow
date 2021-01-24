from .. import db, app
from .dbhandler import Movie, Category, MovieCategoryScores, MoviePersonScores, Person
from sqlalchemy.sql import func
import requests
import json
from itertools import islice

tmdb_key = 'db254eee52d0c8fbc70d51368cd24644'

def add_movie(id):
    if get_movie(id):
        return None
    respons = requests.get('http://api.themoviedb.org/3/movie/' + str(id) + '?api_key=' + tmdb_key)
    if respons.status_code != 200:
        return None
    movie = json.loads(respons.text)
    genres = movie['genres']
    genres.append({'id': 0, 'name': ''})
    m = Movie(id = movie['id'], name = movie['original_title'], poster_path=movie['poster_path'])
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
    for person in mcredits['crew']:
        if person['job'] == 'Director':
            a = MoviePersonScores(score=700)
            p = get_person(person['id'])
            a.movie = m
            a.person = p
            a.job = 1
            p.movies.append(a)
            db.session.add(a)
        elif person['job'] == 'Screenplay' or person['job'] == 'Writing':
            a = MoviePersonScores(score=700)
            p = get_person(person['id'])
            a.movie = m
            a.person = p
            a.job = 2
            p.movies.append(a)
            db.session.add(a)
    for actor in actors:
        a = MoviePersonScores(score=700)
        p = get_person(actor['id'])
        a.movie = m
        a.person = p
        a.job = actor['character']
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
    p = Person(id = person['id'], name = person['name'], score = 700, profile_path=person['profile_path'])
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

def get_random_related_movies():
    m1 = Movie.query.order_by(func.random()).first()
    m2 = Movie.query.order_by(func.random()).first()
    return m1, m2

def get_top_movies_by_category(category_id):
    query = db.session.query(
    MovieCategoryScores,
    func.rank()\
        .over(
            order_by=MovieCategoryScores.score.desc(),
            partition_by=MovieCategoryScores.category_id,
        )\
        .label('rank')
    ).filter(MovieCategoryScores.votes >= 10)
    # now filter
    query = query.filter(MovieCategoryScores.category_id == category_id)
    query = query.order_by(MovieCategoryScores.category_id, 'rank')
    movies = query.all()
    return movies

def get_top_movies_by_person(person_id):
    query = db.session.query(
    MoviePersonScores,
    func.rank()\
        .over(
            order_by=MoviePersonScores.score.desc(),
            partition_by=MoviePersonScores.person_id,
        )\
        .label('rank')
    )
    # now filter
    query = query.filter(MoviePersonScores.person_id == person_id)
    query = query.order_by(MoviePersonScores.person_id, 'rank')
    movies = query.all()
    return movies

def get_category_score(movie_id, category_id):
    query = db.session.query(
    MovieCategoryScores,
    func.rank()\
        .over(
            order_by=MovieCategoryScores.score.desc(),
            partition_by=MovieCategoryScores.category_id,
        )\
        .label('rank')
    )
    # now filter
    query = query.filter(MovieCategoryScores.category_id == category_id)
    query = query.order_by(MovieCategoryScores.category_id, 'rank')
    all_movies = query.subquery()
    new_query = db.session.query(all_movies).filter(all_movies.c.movie_id == movie_id)
    my_movie = new_query.first()
    return my_movie

def get_movie_categories(movie_id):
    categories = Movie.query.filter_by(id=movie_id).first().categories
    return categories

def get_movie_categories_with_score(movie_id):
    categories = Movie.query.filter_by(id=movie_id).first().categories
    c_scores = []
    for category in categories:
        c_score = get_category_score(movie_id, category.category_id)
        c_scores.append((category.category, c_score.rank, c_score.score, c_score.votes, c_score[0]))
    return c_scores

def get_common_categories(movie1, movie2):
    cats = MovieCategoryScores.query.filter(MovieCategoryScores.movie_id.in_([movie1, movie2])).group_by(MovieCategoryScores.category_id).having(func.count(MovieCategoryScores.category_id) > 1).all()
    categories = []
    for cat in cats:
        categories.append(cat.category.serialize)
    return categories

def get_people_score(movie_id, person_id):
    query = db.session.query(
    MoviePersonScores,
    func.rank()\
        .over(
            order_by=MoviePersonScores.score.desc(),
            partition_by=MoviePersonScores.person_id,
        )\
        .label('rank')
    )
    # now filter
    query = query.filter(MoviePersonScores.person_id == person_id)
    query = query.order_by(MoviePersonScores.person_id, 'rank')
    all_movies = query.subquery()
    new_query = db.session.query(all_movies).filter(all_movies.c.movie_id == movie_id)
    my_movie = new_query.first()
    return my_movie

def get_movie_people(movie_id):
    people = MoviePersonScores.query.filter_by(movie_id=movie_id).all()
    peoplewi = {
        'actor' : [],
        'director'   : [],
        'writer'    : []
    }
    for person in people:
        p_score = get_people_score(movie_id, person.person_id)
        peoplewi[convert_job(person.job)].append((person.person, p_score.rank, p_score.score, person.job, p_score.votes, p_score[0]))
        
    return peoplewi

def convert_job(job):
    if job == '1':
        return 'director'
    elif job == '2':
        return 'writer'
    else:
        return 'actor'

def get_common_people(movie1, movie2):
    myQuery = MoviePersonScores.query.filter(MoviePersonScores.movie_id.in_([movie1, movie2])).group_by(MoviePersonScores.movie_id, MoviePersonScores.person_id).subquery()
    peps = db.session.query(myQuery).group_by(myQuery.c.person_id).having(func.count(myQuery.c.person_id) > 1).all()
    people = []
    for pep in peps:
        person = get_person(pep[2])
        people.append(person.serialize)
    return people


def vote_for(win, lose):
    #Set score for all common categories
    common = get_common_categories(win, lose)
    for category in common:
        winner = MovieCategoryScores.query.filter_by(movie_id = win, category_id = category['id']).first()
        loser = MovieCategoryScores.query.filter_by(movie_id = lose, category_id = category['id']).first()
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
        winner = MoviePersonScores.query.filter_by(movie_id = win, person_id = person['id']).first()
        loser = MoviePersonScores.query.filter_by(movie_id = lose, person_id = person['id']).first()
        probW = 1/(1 + (10**((loser.score - winner.score)/400)))
        probL = 1-probW
        winner.score = winner.score + (32*(1 - probW))
        loser.score = loser.score + (32*(0 - probL))
        winner.votes +=1
        loser.votes += 1
        db.session.commit()