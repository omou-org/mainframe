import os

# ===============
# Django Settings
# ===============

# much secure
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")

DEBUG = True

ALLOWED_HOSTS = [
    "mainframe-dev.us-west-1.elasticbeanstalk.com",
    "api.omoulearning.net",
    "localhost",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "mainframe",
        "USER": "postgres",
        "PASSWORD": DATABASE_PASSWORD,
        "HOST": "mainframe.crjrqgmavbsy.us-west-2.rds.amazonaws.com",
        "PORT": "5432",
    },
}
SECRET_KEY = os.environ.get("SECRET_KEY")
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
