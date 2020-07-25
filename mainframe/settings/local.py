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
SENDGRID_API_KEY = "dORnXaTiST2TGYpDuA7q3w"
