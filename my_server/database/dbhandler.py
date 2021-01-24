from .. import db, login_manager, app
from flask_login import UserMixin, current_user
from sqlalchemy.orm import relationship
from sqlalchemy.orm import column_property


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
    poster_path = db.Column(db.String(30))
    categories = relationship("MovieCategoryScores", back_populates="movie")
    people = relationship("MoviePersonScores", back_populates="movie")

    @property
    def serialize(self):
        return {
            'id'    : self.id,
            'name'  : self.name,
            'poster_path' : self.poster_path
        }

    def __repr__(self):
        return f'Movie: {self.name}'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))
    movies = relationship("MovieCategoryScores", back_populates="category")

    @property
    def serialize(self):
        return {
            'id'    : self.id,
            'name'  : self.name
        }

    def __repr__(self):
        return f'Category: {self.name}'

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable = False)
    score = db.Column(db.Integer(), nullable = False)
    profile_path = db.Column(db.String(30))
    movies = relationship("MoviePersonScores", back_populates="person")

    @property
    def serialize(self):
        return {
            'id'    : self.id,
            'name'  : self.name,
            'profile_path': self.profile_path
        }

    def __repr__(self):
        return f'Movie: {self.name}'

class MovieCategoryScores(db.Model):
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), primary_key=True)
    score = db.Column(db.Integer)
    votes = db.Column(db.Integer)
    category = relationship("Category", back_populates="movies")
    movie = relationship("Movie", back_populates="categories")
    enough_votes = column_property(votes >= 10)

    def __repr__(self):
        return f'Movie: {self.movie_id} Category: {self.category_id} Score: {self.score}'

class MoviePersonScores(db.Model):
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), primary_key=True)
    job = db.Column(db.String(30), primary_key=True) #0 = actor, 1 = director, 2 = writer
    score = db.Column(db.Integer)
    votes = db.Column(db.Integer, default=0)
    person = relationship("Person", back_populates="movies")
    movie = relationship("Movie", back_populates="people")
    enough_votes = column_property(votes >= 10)

    def __repr__(self):
        return f'<Movie: {self.movie_id} Person: {self.person_id}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))




def commitDB():
    db.session.commit()

def resetDB():
    db.drop_all()
    db.create_all()
    