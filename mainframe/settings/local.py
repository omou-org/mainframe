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
        "USER": "admin",
        "PASSWORD": "password",
        "HOST": "localhost",
        "PORT": "5432",
    },
}
SECRET_KEY = "%wd5++=an&!tao#t)sc%cp@x3k6wmsbcrtsw7st*83908z255+"
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY")
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET")
TWILIO_ACCOUNT_SID = 'test'
TWILIO_AUTH_TOKEN = 'test'
