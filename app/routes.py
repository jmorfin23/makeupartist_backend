from app import app, db
from flask import jsonify, request
from app.models import User, Post

@app.route('/')
@app.route('/index')
def index():
    return "This is the make-up artist flask backend."



@app.route('/api/admin-login', methods=['GET'])
def admin_login():

    username = request.headers.get('username')
    password = request.headers.get('password')


    if not username or not password:
        return jsonify({ 'Error #001': 'Error retrieving credentials. Try again.'})

    user = User.query.filter_by(username=username).first()


    if user is None or not user.check_password(password):
        return jsonify({ 'message': 'Error #002: Invalid credentials' })
    
    return jsonify({ 'Success': 'Admin logged in' })


@app.route('/api/admin-register', methods=['GET', 'POST'])
def admin_register():

    username = request.headers.get('username')
    password = request.headers.get('password')


    if not username or not password:
        return jsonify({ 'Error #001': 'Error retrieving credentials. Try again.'})

    u = User(username=username)
    u.set_password(password)

    db.session.add(u)
    db.session.commit()


    return jsonify({ 'Success': 'Admin Registered' })
