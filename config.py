import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # DB 
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False

    # EMAIL 
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = 587
    MAIL_USE_TLS = 1
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = os.environ.get('ADMINS')

    # MAILCHIMP
    MAILCHIMP_API_KEY = os.environ.get('MAILCHIMP_API_KEY')
    MAILCHIMP_USERNAME = os.environ.get('MAILCHIMP_USERNAME')
    ADMIN_NAME = os.environ.get('ADMIN_NAME')

    # AWS
    S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
    S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY')
    S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY')

    # google 
    RECAPTCHA_SECRET = os.environ.get('RECAPTCHA_SECRET')
    RECAPTCHA_VERIFY_URL = os.environ.get('RECAPTCHA_VERIFY_URL')