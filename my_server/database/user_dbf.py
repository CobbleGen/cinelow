from .. import db, app
from .dbhandler import User, MovieUserScores
import my_server.database.pers_movie_dbf as pmf
from flask_login import current_user
from sqlalchemy.sql import func
from sqlalchemy import desc
import secrets
from PIL import Image
import os



#-------------------------------------------------#
#--------------- USER INFORMATION ----------------#
#-------------------------------------------------#

def createUser(uname, email, password):
    new = User(username=uname, email=email, password=password)
    db.session.add(new)
    db.session.commit()

def getUserById(uid):
    user = User.query.filter_by(id=uid).first()
    return user

def getUserByEmail(umail):
    user = User.query.filter(func.lower(User.email) == func.lower(umail)).first()
    return user

def getUserByUname(uname):
    user = User.query.filter_by(username=uname).first()
    return user

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_name = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profilepics', picture_name)

    output_size = (250, 250)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)
    current_user.image_file = picture_name

def get_total_users():
    rows = db.session.query(User).count()
    return rows






#-------------------------------------------------#
#-------------- USER MOVIE INFO ------------------#
#-------------------------------------------------#

def get_user_scores(user_id):
    query = db.session.query(
    MovieUserScores,
    func.rank()\
        .over(
            order_by=MovieUserScores.score.desc(),
            partition_by=MovieUserScores.user_id,
        )\
        .label('rank')
    ).filter(MovieUserScores.votes >= 5)
    query = query.filter(MovieUserScores.user_id == user_id)
    query = query.order_by(MovieUserScores.user_id, 'rank')
    movies = query.all()
    return movies

def get_top_movies(user_id, amount = 30):
    movies = db.session.query(MovieUserScores.movie_id).filter(MovieUserScores.user_id==user_id, MovieUserScores.seen == 1).order_by(MovieUserScores.score.desc()).limit(amount).all()
    return [i[0] for i in movies]

def get_user_total_votes(user_id):
    votes = db.session.query(func.sum(MovieUserScores.votes)).filter(MovieUserScores.user_id == user_id).first()[0]
    if votes:
        return int(votes/2)
    return 0

def get_top_users_by_votes(amount):
    list = db.session.query(MovieUserScores.user_id, (func.sum(MovieUserScores.votes)/2).label('totalvotes'))\
        .group_by(MovieUserScores.user_id).order_by(desc('totalvotes')).limit(amount).all()
    return list

def get_fav_people(user_id, person_type = 0, amount = 10):
    movies = get_top_movies(user_id, 100)
    mentions = {}
    for idx, movie in enumerate(movies):
        people = pmf.get_movie_people(movie)[pmf.convert_job(str(person_type))]
        for m in people:
            pid = m[0].id
            val = mentions.setdefault(pid, abs(100-idx))
            mentions[pid] = val+ abs(100-idx)
    toplist = [(0,0)]
    for m in mentions:
        if mentions[m] < toplist[-1][1]: continue
        for i, p in enumerate(toplist):
            if i >= amount: break
            if p[1] < mentions[m]:
                toplist.insert(i, (m, mentions[m]))
                break
    toplist.remove((0,0))
    return toplist[0:amount]

def total_user_votes():
    votes = db.session.query(func.sum(MovieUserScores.votes)).first()[0]/2
    return int(votes)