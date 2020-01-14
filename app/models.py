from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref=db.backref('user', lazy='joined'))

    #setup password hash methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    #setup password check method
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Post(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # for logins
    type_id = db.Column(db.Integer)
    url = db.Column(db.String(250))
    date_posted = db.Column(db.DateTime, default=datetime.now().date())
