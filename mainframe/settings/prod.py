import os

# ===============
# Django Settings
# ===============

DEBUG = True

ALLOWED_HOSTS = [
    "mainframe-dev.us-west-1.elasticbeanstalk.com",
    "api.omoulearning.net",
    "localhost",
    "172.31.13.236",
]

DATABASES = {
    "default": {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['RDS_DB_NAME'],
        'USER': os.environ['RDS_USERNAME'],
        'PASSWORD': os.environ['RDS_PASSWORD'],
        'HOST': os.environ['RDS_HOSTNAME'],
        'PORT': os.environ['RDS_PORT'],
    },
}
SECRET_KEY = os.environ.get("SECRET_KEY")
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
