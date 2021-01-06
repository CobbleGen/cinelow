from flask import request, url_for, Blueprint, render_template
from my_server import app

main = Blueprint('main', __name__)

@app.route('/')
def start():
    return render_template('index.html')