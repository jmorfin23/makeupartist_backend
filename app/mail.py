from flask_mail import Message
from app import app, mail
from flask import render_template
from threading import Thread


#create a new thread for sending email/
def async1(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper

#sending email with new thread/
@async1
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def sendEmail(name, email, phone, subj, message, sender="app.config['ADMINS'][0]"):
    msg = Message(
        subject=subj,
        sender=sender,
        recipients=[email]
    )
    msg.html = render_template('/mail.html', name=name, message=message, phone=phone, email=email, subj=subj)
    
    send_async_email(app, msg)

def sendResetPassword(email, html_body): 
    msg = Message(
        subject='Reset Password', 
        sender='noreply@demo.com', 
        recipients=[email]
    )
    msg.html = html_body
    send_async_email(app, msg)



    
    