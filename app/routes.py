from app import app, db
from flask import jsonify, request
from app.models import User, Post
from app.mail import sendEmail




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

    return jsonify({ 'Success': 'Admin logged in', 'username': user.username,
    'id': user.id
    })


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




@app.route('/api/contact', methods=['POST'])
def contact():
    try:
        name = request.headers.get('name')
        email = request.headers.get('email')
        phone = request.headers.get('phone')
        subject = request.headers.get('subject')
        message = request.headers.get('message')

        sendEmail(name=name, email=email, phone=phone, subj=subject, message=message)

        return jsonify({ 'Success': 'message sent'})
    except:
        return jsonify({ 'error': { 'message:': 'error in contact route. Please ask for assistance.' } })


@app.route('/api/image-save', methods=['POST'])
def post():
    admin = request.headers.get('admin')
    url = request.headers.get('image')
    type = request.headers.get('type')

    user = User.query.filter_by(username=admin).first()

    if not user:
        return jsonify({ 'error': {'message': '#004 User was not found'}})
    if not type or not url:
        return jsonify({ 'error': {'message': 'There was an error retrieving type or url. Please ask for assistance.'}})

    #can definitely make this more efficient, think about front end cleanup as well//
    if type.lower() == 'wedding':
        typeID = 1
    if type.lower() == 'hairstyle':
        typeID = 2
    if type.lower() == 'commercial':
        typeID = 3
    if type.lower() == 'studio':
        typeID = 4

    post = Post(user_id=user.id, type_id=typeID, url=url)

    db.session.add(post)
    db.session.commit()

    return jsonify({ 'success': 'Image saved' })



#method for retrieving specific or all types of images//
@app.route('/api/retrieve-images')
def retrieveImage():
    try:
        p = Post.query.all()

        data = []
        for p1 in p:
            data.append(p1.url)
        return jsonify({ 'success': {'data': data}})
    except:
        return jsonify({ 'error': { 'message': 'Error retrieving all posts.' }})

@app.route('/api/specific-image')
def specific():
    pass


@app.route('/api/newsletter', methods=['POST'])
def newsletter():
    #grab email for newletter signup
    print('**')
    print('**')
    print('inside newletter api');
    print('**')
    print('**')


    return jsonify({ 'success': { 'message': 'You have successfully subscribed to my Newsletter! Thank you.' }})
