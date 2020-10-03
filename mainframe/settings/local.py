import os

# ===============
# Django Settings
# ===============

DEBUG = True

ALLOWED_HOSTS = [
    "*",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "mainframe",
        "USER": "postgres",
        "PASSWORD": "ryan1234",
        "HOST": "localhost",
        "PORT": "5432",
    },
}
SECRET_KEY = "%wd5++=an&!tao#t)sc%cp@x3k6wmsbcrtsw7st*83908z255+"
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
