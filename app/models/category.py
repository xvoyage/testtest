from .. import db
from sqlalchemy.sql.expression import func
from .movie import Movie

class Category(db.Model):
    __tablename__ = 'categorys'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    pid = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.Text)
    sortnum = db.Column(db.Integer)
    movies = db.relationship('Movie', backref='category',lazy='dynamic')
    # name_pre = db.Column(db.String(64), nullable=False)
    # user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<Tag %r>' % self.name


    @property
    def name2up(self):
        return self.name;
    
    @name2up.setter
    def name2up(self, name):
        self.name = name.upper()
        

    def check_name(self):
        if self.name is not None:
            c = Category.query.filter_by(name=self.name).first()

            # if not c or (c.id == self.id):
            #     return True
            if not c:
                return True
        
        return False



