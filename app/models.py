from app import app, db
from time import time 
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import jwt 


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('ImagePost', backref=db.backref('user', lazy='joined'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_token(self, expires_in=3600):
        return jwt.encode(
            { 'user_id': self.id, 'exp': time() + expires_in },
            app.config['SECRET_KEY'],
            algorithm='HS256'
        ).decode('utf-8')

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
            
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)
        
    @staticmethod
    def verify_token(token):
        try:
            id = jwt.decode(
                token,
                app.config['SECRET_KEY'],
                algorithm=['HS256']
            )['user_id']
        except:
            return

        return User.query.get(id)
class ImagePost(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # for logins
    type = db.Column(db.String(50))
    url = db.Column(db.String(250))
    date_posted = db.Column(db.DateTime, default=datetime.now().date())

class BlogPost(db.Model):
    blog_post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    author = db.Column(db.String(60))
    url = db.Column(db.String(250))
    path = db.Column(db.String(150))
    content = db.Column(db.Text)
    comments = db.relationship('Comment', backref=db.backref('blogpost', lazy='joined'))
    date_posted = db.Column(db.String(50))

class Comment(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog_post.blog_post_id'))
    name = db.Column(db.String(64))
    message = db.Column(db.String(250))
    date_posted = db.Column(db.DateTime, default=datetime.now().date())
