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
        #retrieve login data
        userData = request.headers.get('data')

        #convert to data to python object
        userData = json.loads(userData)

        #retrieve user
        user = User.query.filter_by(username=userData['username']).first()

        if user is None or not user.check_password(userData['password']):
            return jsonify({ 'error': 'Error #002: Invalid credentials', 'data': { 'status': False } })

        #set user data
        data = {
            'id': user.id,
            'username': user.username,
            'status': True
        }
        return jsonify({ 'success': 'Admin logged in', 'data': data })
    except:
        return jsonify({ 'error': "Error #001 in login.", 'data': { 'status': False }})
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
        imageInfo = request.headers.get('imageInfo')

        #convert to data to python object
        imageInfo = json.loads(imageInfo)

        user = User.query.filter_by(username=imageInfo['admin']).first()

        if not user:
            return jsonify({ 'error': {'message': '#004 User was not found'}})

        #can definitely make this more efficient, think about front end cleanup as well//
        if imageInfo['uploadType'].lower() == 'wedding':
            typeID = 1
        if imageInfo['uploadType'].lower() == 'hairstyle':
            typeID = 2
        if imageInfo['uploadType'].lower() == 'commercial':
            typeID = 3
        if imageInfo['uploadType'].lower() == 'studio':
            typeID = 4

        post = Post(user_id=user.id, type_id=typeID, url=imageInfo['cloudURL'])

        db.session.add(post)
        db.session.commit()

        return jsonify({ 'success': 'Image saved', 'posted_image': post.url })
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
        data.reverse()
        return jsonify({ 'data': data })
    except:
        return jsonify({ 'error': { 'message': 'Error #005 retrieving posts.' }})

@app.route('/api/image-delete', methods=['GET', 'POST'])
def deleteImage():

    #retrieve image url from headers
    imageURL = request.headers.get('imageURL')

    print("**")
    print("**")
    print(imageURL)
    print("**")
    print("**")

    # #query the database for that image to delete
    d = Post.query.filter_by(url=imageURL).first()

    if not d:
        return jsonify({ 'error': 'Could not retrieve that image from the database.' })

    db.session.delete(d)
    db.session.commit()

    return jsonify({ 'deleted': d.url })


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
