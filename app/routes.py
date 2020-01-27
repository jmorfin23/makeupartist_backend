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

    try:
        #request data
        userData = request.headers.get('data')
        #convert to data to python object
        userData = json.loads(userData)

        if not userData['username'] or not userData['password']:
            return jsonify({ 'Error #001': 'Error retrieving credentials. Try again.'})

        user = User.query.filter_by(username=userData['username']).first()

        if user is None or not user.check_password(userData['password']):
            return jsonify({ 'message': 'Error #002: Invalid credentials' })

        data = {
            'id': user.id,
            'username': user.username,
            'status': True
        }
        return jsonify({ 'success': 'Admin logged in', 'data': data })
    except:
        return jsonify({ 'error': { 'message': "Error #001 in login." }})
# ================================================= #
#use this to register admins username and password
#tokens?
@app.route('/api/admin-register', methods=['GET', 'POST'])
def admin_register():

    try:
        username = request.headers.get('username')
        password = request.headers.get('password')


        if not username or not password:
            return jsonify({ 'error': 'Error retrieving credentials. Try again.'})

        u = User(username=username)
        u.set_password(password)

        db.session.add(u)
        db.session.commit()


        return jsonify({ 'success': 'Admin Registered' })
    except:
        return jsonify({ 'error': { 'message': "Error #002 in registering." } })
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
        return jsonify({ 'error': { 'message:': 'Error #003 in contact.' } })


@app.route('/api/image-save', methods=['POST'])
def post():

    try:
        admin = request.headers.get('admin')
        url = request.headers.get('image')
        type = request.headers.get('type')

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
        return jsonify({ 'error': { 'message': 'Error #004 in save-image.'}})


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
        return jsonify({ 'error': { 'message': 'Error #005 retrieving posts.' }})

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
        return jsonify({ 'error': { 'message': 'Error #007 could not subscribe to newletter.' } })


@app.route('/api/add-blogpost', methods=['GET', 'POST'])
def addBlogPost():
    print('**')
    print('**')
    print('**')
    print('**')
    print('**')
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


@app.route('/api/get-blogpost', methods=['GET'])
def getBlogPost():

    try:
        #query database for all blog posts
        blogPost = BlogPost.query.all();

        #list to store and send data to frontend
        data = []

        #iterate through posts
        for p in blogPost:
            data.append({'id': p.blog_post_id, 'title': p.title, 'author': p.author, 'url': p.url, 'content': p.content, 'data_posted': p.date_posted})
        #query database for the post ID
        return jsonify({ 'data': data })
    except:
        return jsonify({ 'error': { 'message': 'Error #009 in get blog-post.' } })
