from app import app, db
from flask import jsonify, request
from app.models import User, Post, BlogPost, Comment
from app.mail import sendEmail
import json

ADMIN_NAME='LUCY JONES'


@app.route('/')
@app.route('/index')
def index():
    return "This is the make-up artist flask backend."



@app.route('/api/admin-login', methods=['GET', 'POST'])
def admin_login():

    username = request.headers.get('username')
    password = request.headers.get('password')


    if not username or not password:
        return jsonify({ 'Error #001': 'Error retrieving credentials. Try again.'})

    user = User.query.filter_by(username=username).first()

    if user is None or not user.check_password(password):
        return jsonify({ 'message': 'Error #002: Invalid credentials' })

    return jsonify({ 'success': 'Admin logged in', 'username': user.username,
    'id': user.id
    })

# ================================================= #
#use this to register admins username and password
#tokens?
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


    return jsonify({ 'success': 'Admin Registered' })

# ================================================= #


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

    try:
        admin = request.headers.get('admin')
        url = request.headers.get('image')
        type = request.headers.get('type')
        print(admin)
        print(url)
        print(type)

        user = User.query.filter_by(username=admin).first()

        if not user:
            return jsonify({ 'error': {'message': '#004 User was not found'}})
        if type == 'null':
            return jsonify({ 'error': {'message': 'Please select a type.'}})

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
    except:
        return jsonify({ 'error': { 'message': 'Retrieving all parameters. Please try again.'}})


#method for retrieving specific or all types of images//
@app.route('/api/retrieve-images', methods=['GET', 'POST'])
def retrieveImage():
    try:
        p = Post.query.all()

        data = []
        for p1 in p:
            data.append(p1.url)
        return jsonify({ 'data': data })
    except:
        return jsonify({ 'error': { 'message': 'Error retrieving all posts.' }})

@app.route('/api/specific-image')
def specific():
    pass


@app.route('/api/sub-newsletter', methods=['POST'])
def newsletter():

    try:
        #grab email for newletter signup
        email = request.headers.get('email')

        return jsonify({ 'success': { 'message': 'You have successfully subscribed to my Newsletter! Thank you.' }})
    except:
        return jsonify({ 'error': { 'message': 'Error, could not subscribe to newletter.' } })


@app.route('/api/add-blogpost', methods=['GET', 'POST'])
def addBlogPost():

    #retrieve blog post data from frontend
    postInfo = request.headers.get('postInfo')

    #convert to data to python object
    postInfo = json.loads(postInfo)

    print(postInfo['title'])
    print(postInfo['url'])
    print(postInfo['text'])

    if not postInfo['title'] or not postInfo['title'] or not postInfo['url']:
        return jsonify({ 'error': { 'message': 'could not retrieve all parameters.' }})

    #post blogpost data to database
    blogPost = BlogPost(title=postInfo['title'], author=ADMIN_NAME, url=postInfo['url'], content=postInfo['text'])

    #ADD & COMMIT blogpost to database
    db.session.add(blogPost)
    db.session.commit()

    return jsonify({ 'success': {'message': 'successfully posted blog post.' }})


@app.route('/api/get-blogpost', methods=['GET', 'POST'])
def getBlogPost():

    id = request.headers.get('post_id')

    #query database for the post ID
    return jsonify({ 'success': { 'data': 'data goes here' } })
