from flask_mail import Message
from app import app, mail
from flask import render_template
from threading import Thread


# EMAIL THREAD
def async1(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper

# SEND EMAIL 
@async1
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def sendEmail(name, email, phone, subj, message, sender="app.config['ADMINS']"):
    msg = Message(
        subject=subj,
        sender=sender,
        recipients=[app.config['ADMINS']
    )
    msg.html = render_template('/mail.html', name=name, message=message, phone=phone, email=email, subj=subj)
    
    send_async_email(app, msg)

def sendResetPassword(email, html_body): 
    msg = Message(
        subject='Reset Password', 
        sender=app.config['ADMINS'], 
        recipients=[email]
    )
    msg.html = html_body
    send_async_email(app, msg)



    
    