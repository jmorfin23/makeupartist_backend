from app import app, db
from flask import jsonify, request
from app.models import User, ImagePost, BlogPost, Comment
from app.mail import sendEmail
from sensinfo import MAILCHIMP_API_KEY, MAILCHIMP_USERNAME, ADMIN_NAME
import json, requests




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


#contact page route
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

#saving an image
@app.route('/api/image-save', methods=['POST'])
def post():

    try:
        imageInfo = request.headers.get('imageInfo')

        #convert to data to python object
        imageInfo = json.loads(imageInfo)

        user = User.query.filter_by(username=imageInfo['admin']).first()

        if not user:
            return jsonify({ 'error': '#004 User was not found', 'status': False })

        post = ImagePost(user_id=user.id, type=imageInfo['uploadType'].lower(), url=imageInfo['cloudURL'])

        db.session.add(post)
        db.session.commit()

        #return new images array
        images = ImagePost.query.all()

        return jsonify({ 'success': 'Image saved', 'posted_image': {'url': post.url, 'type': post.type}, 'status': True, 'newLength':  len(images)})
    except:
        return jsonify({ 'error': 'Error #004 in save-image.', 'status': False})




#retrieve all images
@app.route('/api/retrieve-images', methods=['GET', 'POST'])
def retrieveImage():
    try:
        images = ImagePost.query.all()


        #make a list of dictionaries with url and type
        data = [{'url': i.url, 'type': i.type, 'id': i.post_id} for i in images]

        return jsonify({ 'data': data[::-1] })
    except:
        return jsonify({ 'error': { 'message': 'Error #005 retrieving posts.' }})

#deleting images 
@app.route('/api/image-delete', methods=['GET', 'POST'])
def deleteImage():

    try:
        #retrieve image url from headers
        id = request.headers.get('id')

        # #query the database for that image to delete
        d = ImagePost.query.filter_by(post_id=id).first()
        
        if not d:
            return jsonify({ 'error': 'Could not retrieve that image from the database.', 'status': False})

        db.session.delete(d)
        db.session.commit()
        
        images = ImagePost.query.all()

        return jsonify({ 'status': True, 'deletedImage': d.url, 'newLength':  len(images) })
    except:
        return jsonify({ 'error': 'Could not delete image from database.', 'status': False, 'newLength': len(images) })

#subscribing to newsletter 
@app.route('/api/sub-newsletter', methods=['POST'])
def newsletter():

    try:
        #grab email for newletter signup
        email = request.headers.get('email')

        return jsonify({ 'success': { 'message': 'You have successfully subscribed to my Newsletter! Thank you.' }})
    except:
        return jsonify({ 'error': { 'message': 'Error #007 could not subscribe to newletter.' } })

#this needs to be addressed. 
@app.route('/api/add-blogpost', methods=['GET', 'POST'])
def addBlogPost():
    
    #retrieve blog post data from frontend
    postInfo = request.headers.get('postInfo')

    #convert to data to python object
    postInfo = json.loads(postInfo)

    if not postInfo['title'] or not postInfo['title'] or not postInfo['url']:
        return jsonify({ 'error': { 'message': 'could not retrieve all parameters.' }})

    #delete any whitespace in titles 
    postInfo['title'] = postInfo['title'].strip()
    alist = postInfo['title'].split(" ")
    alist = list(filter(lambda x: False if x == '' else True , alist))
    postInfo['title'] = ''.join(alist)

    #post blogpost data to database
    blogPost = BlogPost(title=postInfo['title'], author=ADMIN_NAME, url=postInfo['url'], content=postInfo['text'])
    
    #ADD & COMMIT blogpost to database
    db.session.add(blogPost)
    db.session.commit()
   
    return jsonify({ 'success': {'message': 'successfully posted blog post.' }})

#retrieving all blogposts 
@app.route('/api/get-blogpost', methods=['GET'])
def getBlogPost():

    try:
        #query database for all blog posts
        blogPost = BlogPost.query.all();
        
        #list of blogpost info 
        data = [{'id': p.blog_post_id, 'title': p.title, 'author': p.author, 'url': p.url, 'content': p.content, 'date_posted': p.date_posted} for p in blogPost]

        for i in range(len(data)): 
            data[i]['title'] = data[i]['title'].strip()
            alist = postInfo['title'].split(" ")
            link = '-'.join(alist) 


        #query database for the post ID
        return jsonify({ 'data': data[::-1] })
    except:
        return jsonify({ 'error': { 'message': 'Error #009 in get blog-post.' } })

#retrieving single blogpost
@app.route('/api/single-post', methods=['GET'])
def getSinglePost(): 
    
    id = request.headers.get('id')
    
    post = BlogPost.query.filter_by(blog_post_id=id).first()

    data = {
        'id': post.blog_post_id, 
        'author': post.author,
        'url': post.url,
        'title': post.title, 
        'date': post.date_posted, 
        'content': post.content, 
        'comments': post.comments
    }

    return jsonify({ 'success': data })

@app.route('/api/delete-blog-post', methods=['GET'])
def deleteBlogPost(): 
    print('inside delete blogpost')

    id = request.headers.get('id')

    if not id: 
        return jsonify({'error': 'delete unsuccessful'})

    post = BlogPost.query.filter_by(blog_post_id=id).first()

    if not post: 
        return jsonify({'error': 'delete unsuccessful'})
    
    db.session.delete(post)
    db.session.commit()

    return jsonify({'success': 'Blog post successfully deleted', 'id': post.blog_post_id})

@app.route('/api/mailchimp', methods=['GET'])
def getData(): 

    url = 'https://us4.api.mailchimp.com/3.0/automations/' #50e64ce39f/emails/6376bb24f5/queue

    auth = (MAILCHIMP_USERNAME, MAILCHIMP_API_KEY)

    headers = {'Content-Type': 'application/json'}

    # body = {'email_address': 'jmorfin7577@yahoo.com'}

    response = requests.get(url, auth=auth, headers=headers)

    return jsonify({ 'response': response.json() })
