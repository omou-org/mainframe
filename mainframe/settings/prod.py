# ===============
# Django Settings
# ===============

# much secure
DATABASE_PASSWORD = "a22jAxkqPfv6"

DEBUG = False

ALLOWED_HOSTS = [
    "3.19.70.245",
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
SECRET_KEY = "%wd5++=an&!tao#t)sc%cp@x3k6wmsbcrtsw7st*83908z255+"
