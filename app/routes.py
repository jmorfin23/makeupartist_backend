from app import app, db
from flask import jsonify, request, render_template
from sqlalchemy import desc
from app.models import User, ImagePost, BlogPost, Comment
from app.mail import sendEmail, sendResetPassword
from app.forms import ResetPasswordForm
import json, requests
import jwt
from time import time 




@app.route('/')
@app.route('/index')
def index():
    print(time())
    return "This is the make-up artist flask backend."


@app.route('/api/admin-auth', methods=['GET', 'POST'])
def user_auth():
    try: 
        token = request.headers.get('token')

        user = User.verify_token(token)
        
        if not user:
            return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'token expired ' })

        return jsonify({ 'status': 'expired', 'data': False, 'message': '', 'error': 'token expired' })
        return jsonify({ 'status': 'ok', 'data': [], 'message': '', 'error': '' })
    except: 
        return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'Cannot authouthorize user' })

@app.route('/api/admin-login', methods=['GET', 'POST'])
def admin_login():

    try:
        # Retrieve token from headers
        token = request.headers.get('token')

        # verify token 
        data = jwt.decode(
            token,
            app.config['SECRET_KEY'],
            algorithm=['HS256']
        )
        
        # query db to get user and check pass
        user = User.query.filter_by(username=data['username']).first()

        if user is None or not user.check_password(data['password']):
            return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'Invalid credentials' })
            # return jsonify({ 'error': 'Error #002: Invalid credentials', 'data': { 'status': False } })
        
        return jsonify({ 'status': 'ok', 'data': user.get_token(), 'message': '', 'error': '' })
        # return jsonify({ 'success': 'Admin logged in', 'data': data })
    except:
        return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'Cannot log in' })
        # return jsonify({ 'error': "Error #001 in login.", 'data': { 'status': False }})
# ================================================= #
#use this to register admins username and password
#tokens?
@app.route('/api/admin-register', methods=['GET', 'POST'])
def admin_register():

    try:
        # Get token
        token = request.headers.get('token')

        # Decode token 
        data = jwt.decode(
            token,
            app.config['SECRET_KEY'],
            algorithm=['HS256']
        )

        # Add user to db 
        user = User(username=data['username'])
        user.set_password(data['password'])

        # Update db
        db.session.add(user)

        db.session.commit()
        return jsonify({ 'status': 'ok', 'data': user.get_token(), 'message': '', 'error': '' })
        # return jsonify({ 'success': 'Admin Registered', 'data': { 'status': False } })
    except:
        return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'Cannot register user' })
        # return jsonify({ 'error': { 'message': "Error #002 in registering.", 'data': { 'status': False } } })
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

        return jsonify({ 'success': 'Image saved', 'posted_image': {'id': post.post_id, 'url': post.url, 'type': post.type}, 'status': True, 'newLength':  len(images)})
    except:
        return jsonify({ 'error': 'Error #004 in save-image.', 'status': False})




# Retrieve all images
@app.route('/api/retrieve-images', methods=['GET', 'POST'])
def retrieveImage():
    try:
        images = ImagePost.query.all()

        #make a list of dictionaries with url and type
        data = [{'url': i.url, 'type': i.type, 'id': i.post_id} for i in images]
        return jsonify({'status': 'ok', 'data': data[::-1], 'message': '', 'error': '.' })
        return jsonify({ 'data': data[::-1] })
    except:
        return jsonify({ 'error': { 'message': 'Error #005 retrieving posts.' }, 'data': [] })

#deleting images 
@app.route('/api/image-delete', methods=['GET', 'POST'])
def deleteImage():

    try:
        # Retrieve id from headers
        id = request.headers.get('id')

        #  Get image to delete
        d = ImagePost.query.filter_by(post_id=id).first()
        
        if not d:
            return jsonify({ 'error': 'Could not retrieve that image from the database.', 'status': False})

        db.session.delete(d)
        db.session.commit()
        
        images = ImagePost.query.all()
        print('inside image delete')
        print('inside image delete')
        print('inside image delete')
        print('inside image delete')
        print('inside image delete')
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
    try: 
        # Retrieve blog post data from headers
        postInfo = request.headers.get('postInfo')

        # Convert python object
        postInfo = json.loads(postInfo)

        if not postInfo['title'] or not postInfo['text'] or not postInfo['url']:
            return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'Cannot get all required parameters' })

        # ** implement flask - slugify ** 
        #delete any extra whitespace in titles 
        postInfo['title'] = postInfo['title'].strip()
        alist = postInfo['title'].split(" ")
        alist = list(filter(lambda x: False if x == '' else True , alist))
        postInfo['title'] = ' '.join(alist)

        #remove special characters for URL link 
        alphanumeric = ""
        for character in postInfo['title']:
            if character.isalnum() or character == ' ':
                alphanumeric += character
        alphanumeric = alphanumeric.strip()
        alist = alphanumeric.split(" ")
        link = '-'.join(alist)
        postInfo['link'] = link.lower()

        #post blogpost data to database #path and date 
        blogPost = BlogPost(
            title=postInfo['title'],
            author=app.config['ADMIN_NAME'],
            path= postInfo['link'], 
            url=postInfo['url'],
            content=postInfo['text'], 
            date_posted=postInfo['date']
        )
        
        db.session.add(blogPost)
        db.session.commit()

        # return jsonify({ 'success': {'message': 'successfully posted blog post.' }})
        return jsonify({ 'status': 'ok', 'data': [], 'message': 'Blog post is posted', 'error': '' })
    except: 
        return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'Cannot add blog post' })
    
#retrieving all blogposts 
@app.route('/api/get-blogpost', methods=['GET'])
def getBlogPost():

    try: 
        #query database for all blog posts
        blogPost = BlogPost.query.all()
    
        if not blogPost: 
            return jsonify({ 'status': 'ok', 'data': [], 'message': 'No blog posts', 'error': '' })

        #list of blogpost info 
        data = [{'id': p.blog_post_id, 'title': p.title, 'author': p.author, 'url': p.url, 'path': p.path, 'content': p.content, 'date_posted': p.date_posted} for p in blogPost]
        
        #query database for the post ID
        return jsonify({ 'status': 'ok', 'data': data[::-1], 'message': '', 'error': '' })
    except: 
        return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'Could not retrieve blogpost data' })

# Retrieve set number of blogposts 
@app.route('/api/get-requested-number-blogpost')
def get_requested_number_blogpost(): 
    try: 
        # Number from headers 
        n = request.headers.get('number')
        
        if not n: 
            return jsonify({'status': 'error', 'data': [], 'message': '', 'error': 'Number not retrievable' })
        
        # Query database return recent results specified by user 
        posts = BlogPost.query.order_by(desc(BlogPost.blog_post_id)).limit(n).all()
    
        if not posts: 
            return jsonify({'status': 'ok', 'data': [], 'message': 'No blog posts', 'error': ''})
    
        #add information to list of dictionaries
        blog_posts = [{'id': p.blog_post_id, 'title': p.title, 'author': p.author, 'url': p.url, 'path': p.path, 'content': p.content, 'date_posted': p.date_posted} for p in posts]
    
        return jsonify({ 'status': 'ok', 'data': blog_posts, 'message': '', 'error': ''})
    except:
        return jsonify({'status': 'error', 'data': [], 'message': '', 'error': 'Could not get requested posts'})



#retrieving single blogpost
@app.route('/api/single-post', methods=['GET'])
def getSinglePost(): 
    try: 
        path = request.headers.get('path')

        if not path: 
            return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'Could not get path' })
        
        post = BlogPost.query.filter_by(path=path).first()

        if not post: 
            return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'there is no post with that path' })

        data = {
            'id': post.blog_post_id, 
            'author': post.author,
            'url': post.url,
            'path': post.path, 
            'title': post.title, 
            'date': post.date_posted, 
            'content': post.content, 
            'comments': post.comments
        }

        #logic for grabbing next posts 
        blog = BlogPost.query.all()

        nextPosts = []
        flag = False

        for i in range(len(blog)):
            if data['id'] == blog[i].blog_post_id:
                flag = True
                continue   
            
            nextPosts.append({
                'id': blog[i].blog_post_id,
                'title': blog[i].title,
                'date': blog[i].date_posted,
                'path': blog[i].path, 
                'url': blog[i].url
            })
            
            if flag == True and len(nextPosts) >= 3: 
                break
            
            if len(nextPosts) >= 3 and len(blog) != i+2: 
                nextPosts.pop(0)
        
        return jsonify({ 'status': 'ok', 'data': { 'post': data, 'nextPosts': nextPosts }, 'message': '', 'error': '' })
    except: 
        return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'could not get blogpost' })

@app.route('/api/delete-blog-post', methods=['GET'])
def deleteBlogPost(): 
    try: 

        id = request.headers.get('id')

        if not id: 
            return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'Unable to retrieve id' })
        
        post = BlogPost.query.filter_by(blog_post_id=id).first()

        if not post: 
            return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'could not find post to delete' })
        
        # db.session.delete(post)
        # db.session.commit()

        return jsonify({ 'status': 'ok', 'data': True , 'message': 'blog post deleted', 'error': '' })
    except: 
        return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'Cannot delete post' })

@app.route('/api/mailchimp', methods=['GET'])
def getData(): 
    try: 
        #testing still required for this route
        url = 'https://us4.api.mailchimp.com/3.0/automations/' #50e64ce39f/emails/6376bb24f5/queue

        auth = (app.config['MAILCHIMP_USERNAME'], app.config['MAILCHIMP_API_KEY'])

        headers = {'Content-Type': 'application/json'}

        # body = {'email_address': 'jmorfin7577@yahoo.com'}

        response = requests.get(url, auth=auth, headers=headers)

        return jsonify({ 'response': response.json() })
    except:
        return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'could not add to mailchip' })
@app.route('/api/reset-password', methods=['GET', 'POST'])
def resetPassword():

    email = request.headers.get('email')

    #verify if email is in our db
    user = User.query.filter_by(username=email).first()
    
    if not user: 
        return jsonify({'error': 'Invalid email, try again.'})
    
    token = user.get_reset_password_token()

    sendResetPassword(email, html_body=render_template('/reset_password.html', user=user.username, token=token))

    return jsonify({ 'success': 'Check your email to reset your password' })

@app.route('/api/change_password', methods=['GET', 'POST'])
def reset_password():

    #grab new password
    password = request.headers.get('password')
    #grab token and check whether its still valid 
    token = request.headers.get('token')
    #check whether token is valid 
    user = User.verify_reset_password_token(token)

    if not user: 
        return jsonify({'error': 'Token has expired, try again.'})

    user.set_password(password)
    db.session.commit()

    return jsonify({'success': 'Success! Password was reset.'})