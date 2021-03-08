from my_server.database.pers_movie_dbf import get_person
from my_server.database.user_dbf import get_fav_people
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
    return render_template('index.html', fav_actors=fav_actors)