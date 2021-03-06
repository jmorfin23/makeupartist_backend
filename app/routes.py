from app import app, db
from flask import jsonify, request, render_template, url_for
# --- Method / Table imports --- #
from app.models import User, ImagePost, BlogPost, Comment
from app.mail import sendEmail, sendResetPassword
from app.forms import ResetPasswordForm
from app.upload import uploadToS3
# ----------------------------------
import json, requests, os, jwt, boto3, io 
from werkzeug.utils import secure_filename
from sqlalchemy import desc
from time import time 
from slugify import slugify


@app.route('/')
@app.route('/index')
def index():
    return "kathryn Stevens makeup artist backend"

# Authenticate admin 
@app.route('/api/admin-auth', methods=['GET', 'POST'])
def user_auth():
    try: 
        token = request.headers.get("Authorization").split(" ")
          
        if token[0] == "Bearer": 
            
            # Verify admin 
            user = User.verify_token(token[1])
                
            if not user:
                return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'token expired ' })

            return jsonify({ 'status': 'expired', 'data': False, 'message': '', 'error': 'token expired' })
    except: 
        return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'Cannot authouthorize user' })

# Login admin 
@app.route('/api/admin-login', methods=['GET', 'POST'])
def admin_login():
    try:
        if request.authorization: 
            
            # Login credentials 
            username = request.authorization.username
            password = request.authorization.password
    
            # query db to get user and check pass
            user = User.query.filter_by(username=username).first()
           
            if user is None or not user.check_password(password):
                return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'Invalid credentials' })
           
            return jsonify({ 'status': 'ok', 'data': user.get_token(), 'message': '', 'error': '' })
    except:
        return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'Cannot log in' })

# Send contact email 
@app.route('/api/contact', methods=['POST'])
def contact():
    try:
        if request.method == 'POST': 
           
            if request.form: 
                
                # ReCaptcha client token
                token = request.headers.get("Authorization").split(" ")
                
                if token[0] == 'Bearer': 
                    
                    # Verify token 
                    response = requests.post(
                        url=app.config['RECAPTCHA_VERIFY_URL'], 
                        params={
                            'secret': app.config['RECAPTCHA_SECRET'], 
                            'response': token[1]
                        }
                    )
                    
                    result = response.json()

                    # Return error if token verification fails 
                    if response.status_code != 200 or not result['success']: 
                        return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'Token verification failed, try again.' })
                    
                    # Send form data  
                    name = request.form['name']
                    email = request.form['email']
                    subject = request.form['subject']
                    phone = request.form['phone']
                    message = request.form['message']
                    
                    sendEmail(name=name, email=email, phone=phone, subj=subject, message=message)
            
                    return jsonify({ 'status': 'ok', 'data': [], 'message': 'Your message was sent, thank you.', 'error': '' })
    except:
        return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'Your message did not send. Try again.' })

# Add a blogpost 
@app.route('/api/image-save', methods=['POST'])
def post():
    try:
        if request.method == 'POST':
            
            # Admin token 
            token = request.headers.get('Authorization').split(" ")
            
            if token[0] == "Bearer": 
                
                # Verify admin 
                user = User.verify_token(token[1])

                if not user:
                    return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'User was not found' })

                # Get image data 
                image = request.files['file']
                filename = secure_filename(image.filename)
                bucket_name = app.config['S3_BUCKET_NAME']

                # Send to S3 
                status = uploadToS3(image, filename, bucket_name)
                
                if not status: 
                    return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'Cannot upload image to cloud.' })
                    
                # Save url in db w/ upload type 
                image_url = f'https://{bucket_name}.s3.amazonaws.com/{filename}'
                
                upload_type = request.form['upload_type'].lower()
                
                post = ImagePost(user_id=user.id, type=upload_type, url=image_url)
                    
                db.session.add(post)
                db.session.commit()

                return jsonify({ 'status': 'ok', 'data': {'id': post.post_id, 'type': post.type, 'url': post.url}, 'message': 'Image added', 'error': '' })
    except:
        return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'Cannot add image' })

# Retrieve all images
@app.route('/api/retrieve-images', methods=['GET', 'POST'])
def retrieveImage():
    try:
        # Query all images 
        images = ImagePost.query.all()

        data = [{'url': i.url, 'type': i.type, 'id': i.post_id} for i in images]

        return jsonify({'status': 'ok', 'data': data[::-1], 'message': '', 'error': '.' })
    except:
        return jsonify({'status': 'error', 'data': [], 'message': '', 'error': 'Cannot retrieve images' })

# delete an image
@app.route('/api/image-delete', methods=['GET', 'POST'])
def deleteImage():
    try:
        # ID & Admin token 
        id = request.headers.get('id')
        token = request.headers.get('Authorization').split(" ")

        if token[0] == "Bearer": 
            
            # Verify admin 
            user = User.verify_token(token[1])
            
            if not user:
                return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'token expired ' })

            # Image to delete 
            image = ImagePost.query.filter_by(post_id=id).first()
            
            if not image:
                return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'Cannot find image' })

            db.session.delete(image)
            db.session.commit()
            
            return jsonify({ 'status': 'ok', 'data': { 'id': image.post_id }, 'message': 'Image deleted', 'error': '' })
    except:
        return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'Token expired or another issue' })

# Subscribe to newsletter # TODO: WHEN EMAIL LIST IS SET UP 
@app.route('/api/sub-newsletter', methods=['POST'])
def newsletter():
    try:
        if request.json: 

            email = request.json
        
        return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'The newsletter is not yet set-up, try again later.' })
    except:
        return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'Cannot subscribe to newsletter.' })

# Adds blog post 
@app.route('/api/add-blogpost', methods=['POST'])
def addBlogPost():
    try:    
        if request.method == 'POST':
            
            # Admin token  
            token = request.headers.get('Authorization').split(" ")
            
            if token[0] == "Bearer": 
                
                # Verify token 
                user = User.verify_token(token[1])
                
                if not user:
                    return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'token expired ' })
                
                # Send image to S3
                image = request.files['image']
                filename = secure_filename(image.filename)
                bucket_name = app.config['S3_BUCKET_NAME']
                
                status = uploadToS3(image, filename, bucket_name)
                
                if not status: 
                    return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'Cannot upload image to cloud.' })
                
                # Save url in db w/ upload type 
                image_url = f'https://{bucket_name}.s3.amazonaws.com/{filename}'
               
                title = request.form['title']
                date = request.form['date']
                text = request.form['text']
                
                # Create slug from post title 
                created_path = slugify(title)
                
                # Create post 
                blogPost = BlogPost(
                    title=title,
                    author=app.config['ADMIN_NAME'],
                    path=created_path, 
                    url=image_url,
                    content=text, 
                    date_posted=date
                )
                
                # Add post 
                db.session.add(blogPost)
                db.session.commit()
                
                post = BlogPost.query.order_by(desc(BlogPost.blog_post_id)).first()

                return jsonify({ 'status': 'ok', 'data': {'id': post.blog_post_id, 'title': post.title, 'author': post.author, 'url': post.url, 'path': post.path, 'content': post.content, 'date_posted': post.date_posted} , 'message': 'Blog post is posted', 'error': '' })
    except: 
        return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'Cannot add blog post' })
    
# Get all blog posts 
@app.route('/api/get-blogpost', methods=['GET'])
def getBlogPost():

    try: 
        # Get blogposts 
        blogPost = BlogPost.query.all()
    
        if not blogPost: 
            return jsonify({ 'status': 'ok', 'data': [], 'message': 'No blog posts', 'error': '' })

        # Blog info 
        data = [{'id': p.blog_post_id, 'title': p.title, 'author': p.author, 'url': p.url, 'path': p.path, 'content': p.content, 'date_posted': p.date_posted} for p in blogPost]
        
        return jsonify({ 'status': 'ok', 'data': data[::-1], 'message': '', 'error': '' })
    except: 
        return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'Could not retrieve blogpost data' })

# Retrieve set number of blogposts 
@app.route('/api/get-requested-number-blogpost')
def get_requested_number_blogpost(): 
    try: 
        # Number of posts to return 
        n = request.headers.get('number')
        
        if not n: 
            return jsonify({'status': 'error', 'data': [], 'message': '', 'error': 'Number not retrievable' })
        
        # Query db
        posts = BlogPost.query.order_by(desc(BlogPost.blog_post_id)).limit(n).all()
    
        if not posts: 
            return jsonify({'status': 'ok', 'data': [], 'message': 'No blog posts', 'error': ''})
    
        # Blog posts 
        blog_posts = [{'id': p.blog_post_id, 'title': p.title, 'author': p.author, 'url': p.url, 'path': p.path, 'content': p.content, 'date_posted': p.date_posted} for p in posts]
    
        return jsonify({ 'status': 'ok', 'data': blog_posts, 'message': '', 'error': ''})
    except:
        return jsonify({'status': 'error', 'data': [], 'message': '', 'error': 'Could not get requested posts'})

# Get single blog post
@app.route('/api/single-post', methods=['GET'])
def getSinglePost(): 
    try: 
        # Blog post path 
        path = request.headers.get('path')

        if not path: 
            return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'Could not get path' })
        
        # Query db 
        post = BlogPost.query.filter_by(path=path).first()

        if not post: 
            return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'there is no post with that path' })

        # Blog post info 
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

        # Logic for "next-posts" 
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

# Deletes single blog post 
@app.route('/api/delete-blog-post', methods=['GET'])
def deleteBlogPost(): 
    try: 
        # Verify admin 
        token = request.headers.get('Authorization').split(" ")
        id = request.headers.get('id')

        if token[0] == "Bearer": 

            user = User.verify_token(token[1])
            
            if not user:
                return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'token expired ' })

            # Query db 
            post = BlogPost.query.filter_by(blog_post_id=id).first()

            # Delete post 
            db.session.delete(post)
            db.session.commit()

            # Return 'deleted' Post ID --> for UI 
            return jsonify({ 'status': 'ok', 'data': post.blog_post_id , 'message': 'blog post deleted', 'error': '' })
    except: 
        return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'Cannot delete post' })

# Gets blog posts specific to 'page' of blog view 
@app.route('/api/get-next-posts', methods=['GET'])
def getNextPosts(): 
    try: 
        # Page specific blogposts
        page_num = int(request.headers.get('page_num'))
        posts_per_page = int(request.headers.get('posts_per_page'))
    
        if not page_num or not posts_per_page: 
            return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'Cannot get page number or posts per page number' })

        # Query db 
        posts = BlogPost.query.order_by(desc(BlogPost.blog_post_id)).paginate(page_num, posts_per_page, False)
        
        # Blog posts
        blog_posts = [{'id': p.blog_post_id, 'title': p.title, 'author': p.author, 'url': p.url, 'path': p.path, 'content': p.content, 'date_posted': p.date_posted} for p in posts.items]

        return jsonify({ 'status': 'ok', 'data': {'posts': blog_posts, 'info': { 'currentPage': page_num, 'has_next': posts.has_next, 'has_prev': posts.has_prev, 'next_num': posts.next_num, 'prev_num': posts.prev_num} } , 'message': 'blog post deleted', 'error': '' })
    except: 
        return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'Cannot retrieve posts' })

# Admin password reset 
@app.route('/api/reset-password', methods=['POST'])
def resetPassword():
    try: 
        if request.json:
            # Email to verify 
            email = request.json

            # Verify email 
            user = User.query.filter_by(username=email).first()
            
            if not user: 
                return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'invalid email' })
            
            # Send email with reset token 
            token = user.get_reset_password_token()

            sendResetPassword(email, html_body=render_template('/reset_password.html', user=user.username, token=token))

            return jsonify({ 'status': 'ok', 'data': [], 'message': 'Check your email to reset your password', 'error': '' })
    except: 
        return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'Cannot reset password'})

# Changes passoword after admin is verified 
@app.route('/api/change_password', methods=['POST'])
def reset_password():
    try: 
        if request.json: 
            # Verify token
            token = request.headers.get("Authorization").split(" ")
            password = request.json
            
            if token[0] == "Bearer": 

                user = User.verify_reset_password_token(token[1])

                if not user: 
                    return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'Cannot reset password'})

                #Set new password
                user.set_password(password)
                db.session.commit()

                return jsonify({ 'status': 'ok', 'data': [], 'message': 'Success, password was reset', 'error': ''})
    except: 
        return jsonify({ 'status': 'error', 'data': [], 'message': '', 'error': 'Cannot reset password'})

