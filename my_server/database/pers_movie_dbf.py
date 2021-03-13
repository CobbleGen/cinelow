from operator import and_
from sqlalchemy.sql.elements import False_, True_

from sqlalchemy.sql.expression import insert
from .. import db
from .dbhandler import Movie, Category, MovieCategoryScores, MoviePersonScores, Person, MovieUserScores
import my_server.database.user_dbf as uf
from sqlalchemy.sql import func
from sqlalchemy import desc
from sqlalchemy import or_
import math
import requests
import json
import random
from itertools import islice

tmdb_key = 'db254eee52d0c8fbc70d51368cd24644'

def biased_random_number(min, max, bias):
    return min + (max - min) * pow(random.uniform(0, 1), bias)

#-------------------------------------------------#
#------------GET / ADD FUNCTIONS -----------------#
#-------------------------------------------------#

def add_movie(id):
    exi_mov = get_movie(id)
    if exi_mov:
        return exi_mov
    respons = requests.get('http://api.themoviedb.org/3/movie/' + str(id) + '?api_key=' + tmdb_key)
    if respons.status_code != 200:
        return None
    movie = json.loads(respons.text)
    genres = movie['genres']
    genres.insert(0, {'id': 0, 'name': ''})
    m = Movie(id = movie['id'], name = movie['title'], poster_path=movie['poster_path'])
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
    return m

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

def get_movie_categories(movie_id):
    categories = Movie.query.filter_by(id=movie_id).first().categories
    return categories

def get_movie_category_ids(movie):
    out = [ a.category_id for a in movie.categories ]
    return out

def get_common_categories(movie1, movie2):
    cats = db.session.query(MovieCategoryScores.category_id, func.sum(MovieCategoryScores.movie_id))\
        .filter(MovieCategoryScores.movie_id.in_([movie1, movie2]))\
        .group_by(MovieCategoryScores.category_id)\
        .having(func.count(MovieCategoryScores.category_id) > 1).all()
    categories = []
    for cat in cats:
        categories.append(get_category(cat[0]).serialize)
    return categories

def get_common_people(movie1, movie2):
    myQuery = db.session.query(MoviePersonScores.movie_id, MoviePersonScores.person_id).filter(MoviePersonScores.movie_id.in_([movie1, movie2])).group_by(MoviePersonScores.movie_id, MoviePersonScores.person_id).subquery()
    peps = db.session.query(myQuery.c.person_id).group_by(myQuery.c.person_id).having(func.count(myQuery.c.person_id) > 1).all()
    people = []
    for pep in peps:
        person = get_person(pep[0])
        people.append(person.serialize)
    return people

def get_movie_amount():
    rows = db.session.query(Movie).count()
    return rows

def get_all_categories():
    cats = Category.query.all()
    categories = []
    for cat in cats:
        categories.append(cat.serialize)
    return categories




#-------------------------------------------------#
#------- RECOMMENDATIONS / RELEVANCY -------------#
#-------------------------------------------------#

def get_relevant_movie(except_for = []):
    most_watched = get_most_watched_movies(except_for, 1000)
    list_id = math.trunc(biased_random_number(0, len(most_watched), 4))
    return most_watched[list_id][0]

def get_close_movie(movie_id, exclude = [], range = 100):
    movie_score = db.session.query(MovieCategoryScores.score)\
        .filter(MovieCategoryScores.movie_id==movie_id, MovieCategoryScores.category_id==0).first()[0]
    min = movie_score - range/2
    max = movie_score + range/2
    exclude.append(movie_id)
    close = MovieCategoryScores.query.\
        filter(MovieCategoryScores.category_id==0, MovieCategoryScores.score.between(min, max), MovieCategoryScores.movie_id.notin_(exclude))\
            .order_by(func.random()).first()
    return close.movie

def get_random_related_movies(user = None):
    not_seen = []
    if user.is_authenticated:
        not_seen = get_seen_movies(user.id, -1)
        seen = get_seen_movies(user.id, 1)
        top_movs = uf.get_top_movies(user.id)
        prospects = seen + top_movs
        rand_index = random.randint(0, math.trunc((1.4*len(prospects))+15))
        if rand_index < len(prospects):
            movie_id = prospects[rand_index]
        else:
            movie_id = get_relevant_movie(not_seen)
    else:
        movie_id = get_relevant_movie()
    m1 = Movie.query.filter(Movie.id==movie_id).first()
    if random.randrange(0, 5) < 2:
        m2 = get_close_movie(m1.id, not_seen)
        return m1, m2
    respons = requests.get('https://api.themoviedb.org/3/movie/' + str(m1.id) + '/recommendations?api_key=' + tmdb_key + '&language=en-US&page=' + random.choices("12", cum_weights=(0.65, 1.00))[0])
    if respons.status_code != 200:
        return None
    ids = [ r['id'] for r in json.loads(respons.text)['results']]
    m2 = Movie.query.filter(Movie.id.in_(ids), Movie.id.notin_(not_seen)).order_by(func.random()).first()
    if m2 == None:
        m2 = get_close_movie(m1.id, not_seen)
    return m1, m2

###   Not yet implemented or working ###
def get_random_related_movie(to_movie):
    #category_id = to_movie.categories[random.randint(1, len(to_movie.categories)-1)].category_id
    category_ids = [ i.category_id for i in to_movie.categories ]
    person_query = db.session.query(MoviePersonScores.movie_id)\
        .filter(MoviePersonScores.person_id.in_([ p.person_id for p in to_movie.people ])).all()
    people_ids = [ i[0] for i in person_query ]
    movies = db.session.query(MovieCategoryScores.movie_id)\
        .filter(and_(MovieCategoryScores.movie_id.in_(people_ids), MovieCategoryScores.category_id.in_(category_ids))).all()
    return movies

def get_related_movies(movies, exclude = [], amount = 10):
    mentions = {}
    for movie_id in movies:
        respons = requests.get('https://api.themoviedb.org/3/movie/' + str(movie_id) + '/recommendations?api_key=' + tmdb_key + '&language=en-US&page=1')
        if respons.status_code == 200:
            for m in json.loads(respons.text)['results']:
                mid = m['id']
                if mid in exclude: continue
                val = mentions.setdefault(mid, 0)
                mentions[mid] = val+1
    toplist = [(0,0)]
    for key in mentions:
        movie_score = MovieCategoryScores.query.with_entities(MovieCategoryScores.score).filter(MovieCategoryScores.movie_id==key, MovieCategoryScores.category_id == 0).first()
        if movie_score == None:
            continue
        movie_score = movie_score[0]
        rating = ((mentions[key] -1) * movie_score)/4 + movie_score
        movie = (key, rating)
        if len(toplist) >= amount and rating < toplist[amount-1][1]: continue
        for i, m in enumerate(toplist):
            if i >= amount: break
            if m[1] < movie[1]:
                toplist.insert(i, movie)
                break
    toplist.remove((0,0))
    return toplist[0:amount]

def get_user_recommendations(user_id, amount = 10):
    seen = get_seen_movies(user_id, 1)
    user_top = uf.get_top_movies(user_id, 15)
    related = get_related_movies(user_top, seen, amount)
    if len(related) < amount:
        needed = amount-len(related)
        most_watched = get_most_watched_movies([], needed)
        related.extend(most_watched)
    output = []
    for m in related:
        movie = get_movie(m[0])
        output.append(movie.serialize)
    return output


def get_most_watched_movies(dont_include = [], limit = 300):
    mquery = db.session.query(
        MovieUserScores.movie_id,
        func.avg(MovieUserScores.seen)\
        .over(
            partition_by=MovieUserScores.movie_id,
        )\
        .label('average')).filter(MovieUserScores.movie_id.notin_(dont_include)).subquery()
    result = db.session.query(mquery.c.movie_id, mquery.c.average)\
        .order_by(desc(mquery.c.average)).group_by(mquery.c.movie_id, mquery.c.average).limit(limit).all()
    return result


def advanced_recommendations(user_ids = [], categories = [], not_seen = True, amount = 10):
    all_seen = []
    all_tops = []
    for user_id in user_ids:
        all_seen.extend(get_seen_movies(user_id, 1))
        all_tops.extend(uf.get_top_movies(user_id, 10))
    if not categories or -1 in categories: #If any category can be used:
        related = get_related_movies(all_tops, all_seen, amount)
        if len(related) < amount:
            needed = amount-len(related)
            most_watched = get_most_watched_movies([], needed)
            related.extend(most_watched)
        output = []
        for m in related:
            movie = get_movie(m[0])
            output.append(movie.serialize)
        return output
    #If specific categories are requested:
    related = get_related_movies(all_tops, all_seen, amount*5)
    output = []
    for m in related:
        movie = get_movie(m[0])
        if not set(get_movie_category_ids(movie)).isdisjoint(categories):
            output.append(movie.serialize)
    if len(output) < amount:
        top_movs = get_top_movies_by_category(0)
        for m in top_movs:
            if not set(get_movie_category_ids(m[0].movie)).isdisjoint(categories):
                output.append(m[0].movie.serialize)
    return output






#-------------------------------------------------#
#--------- SCORE GETTING / SETTING ---------------#
#-------------------------------------------------#

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
    ).filter(or_(MovieCategoryScores.votes >= 10, MovieCategoryScores.movie_id == movie_id))
    # now filter
    query = query.filter(MovieCategoryScores.category_id == category_id)
    query = query.order_by(MovieCategoryScores.category_id, 'rank')
    all_movies = query.subquery()
    new_query = db.session.query(all_movies).filter(all_movies.c.movie_id == movie_id)
    my_movie = new_query.first()
    return my_movie

def get_movie_categories_with_score(movie_id):
    categories = Movie.query.filter_by(id=movie_id).first().categories
    c_scores = []
    for category in categories:
        c_score = get_category_score(movie_id, category.category_id)
        c_scores.append((category.category, c_score.rank, c_score.score, c_score.votes, c_score[0]))
    return c_scores


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
    people = MoviePersonScores.query.filter_by(movie_id=movie_id).order_by(MoviePersonScores.score.desc()).all()
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

def get_user_score(movie_id, user_id):
    movie = MovieUserScores.query.filter_by(movie_id = movie_id, user_id = user_id).first()
    if movie:
        return movie
    a = MovieUserScores(score = 700, votes = 0, seen = 0)
    a.movie = get_movie(movie_id)
    user = uf.getUserById(user_id)
    a.user = user
    user.movie_scores.append(a)
    db.session.add(a)
    db.session.commit()
    return a

def get_max_score():
    score = db.session.query(MovieCategoryScores.score).filter(MovieCategoryScores.category_id == 0).order_by(desc(MovieCategoryScores.score)).limit(1).first()[0]
    return int(score)




#-------------------------------------------------#
#----------- VOTING AND SEEN MOVIE ---------------#
#-------------------------------------------------#

def vote_for(win, lose, user_id = None):
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
    #Set User score
    if user_id != None:
        winner = get_user_score(win, user_id)
        loser = get_user_score(lose, user_id)
        loser = MovieUserScores.query.filter_by(movie_id = lose, user_id = user_id).first()
        probW = 1/(1 + (10**((loser.score - winner.score)/400)))
        probL = 1-probW
        winner.score = winner.score + (32*(1 - probW))
        loser.score = loser.score + (32*(0 - probL))
        winner.votes +=1
        loser.votes += 1
        winner.seen = 1
    db.session.commit()

def seen_movie(movie_id, user_id, seen):
    get_user_score(movie_id, user_id).seen = seen
    db.session.commit()

def get_seen_movie(movie_id, user_id):
    score = MovieUserScores.query.filter_by(movie_id = movie_id, user_id = user_id).first()
    if score:
        return score.seen
    return 0

def get_seen_movies(user_id, seen_value):
    movies = [ r.movie_id for r in MovieUserScores.query.with_entities(MovieUserScores.movie_id).filter(and_(MovieUserScores.user_id == user_id, MovieUserScores.seen == seen_value))]
    return movies