from flask_login.utils import _get_user
from my_server.database.pers_movie_dbf import get_person
from my_server.database.user_dbf import getUserById, get_fav_people, get_top_users_by_votes
from flask import Blueprint, render_template
from flask_login import current_user
from my_server import app

main = Blueprint('main', __name__)

@app.route('/')
def start():
    fav_actors = []
    if current_user.is_authenticated:
        for i in get_fav_people(current_user.id, 0, 3):
           fav_actors.append(get_person(i[0]).serialize)
    top_user_ids = get_top_users_by_votes(5)
    top_users = []
    for id in top_user_ids:
        top_users.append((getUserById(id[0]).serialize, id[1]))
    return render_template('index.html', fav_actors=fav_actors, top_users=top_users)