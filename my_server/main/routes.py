from my_server.database.pers_movie_dbf import get_person
from random import randint
from my_server.database.user_dbf import get_fav_people
from flask import Blueprint, render_template
from flask_login import current_user
from my_server import app

main = Blueprint('main', __name__)

@app.route('/')
def start():
    fav_actor = -1
    if current_user.is_authenticated:
        fav_actor = get_person( get_fav_people(current_user.id, 0, 4)[randint(0, 3)][0] ).serialize
        print(fav_actor)
    return render_template('index.html', fav_actor=fav_actor)