from .. import db, login_manager, app
from flask_login import UserMixin, current_user
from sqlalchemy.orm import relationship


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable = False, unique=True)
    email = db.Column(db.String(100), nullable = False, unique=True)
    password = db.Column(db.String(20), nullable = False)
    image_file = db.Column(db.String(20), nullable = False, default='default.jpg')

    def __repr__(self):
        return f'User: {self.username}'

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable = False)
    categories = relationship("MovieCategoryScores", back_populates="movie")
    people = relationship("MoviePersonScores", back_populates="movie")

    def __repr__(self):
        return f'Movie: {self.name}'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))
    movies = relationship("MovieCategoryScores", back_populates="category")

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable = False)
    job = db.Column(db.String(64), nullable = False)
    score = db.Column(db.Integer(), nullable = False)
    movies = relationship("MoviePersonScores", back_populates="person")

    def __repr__(self):
        return f'Movie: {self.name}'

class MovieCategoryScores(db.Model):
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), primary_key=True)
    score = db.Column(db.Integer)
    votes = db.Column(db.Integer)
    category = relationship("Category", back_populates="movies")
    movie = relationship("Movie", back_populates="categories")

class MoviePersonScores(db.Model):
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), primary_key=True)
    score = db.Column(db.Integer)
    person = relationship("Person", back_populates="movies")
    movie = relationship("Movie", back_populates="people")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))




def commitDB():
    db.session.commit()

def resetDB():
    db.drop_all()
    db.create_all()
    