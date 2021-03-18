from .. import db
from werkzeug.security import generate_password_hash, check_password_hash
from .. import login_manager
from flask import current_app
import hashlib
# from .tag import Tag
# from .movie import Movie
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64), nullable=False)
    # tags = db.relationship('Tag', backref='author', lazy='dynamic')
    # categorys = db.relationship('Category', backref='category_author', lazy='dynamic')
    # movies = db.relationship('Movie', backref='m_author', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)


    def verify_password(self, password):
        return check_password_hash(self.password_hash,password)


    def __repr__(self):
        return '<User %r>' % self.username

