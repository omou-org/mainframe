import os
from datetime import timedelta

# ===============
# Django Settings
# ===============

DEBUG = True

ALLOWED_HOSTS = [
    "mainframe-dev.us-west-1.elasticbeanstalk.com",
    "mainframe-env.eba-yszaihyi.us-west-1.elasticbeanstalk.com",
    "api.omoulearning.com",
    "development.omoulearning.com",
    "getomou.com",
    "localhost",
    "172.31.0.238",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ["RDS_DB_NAME"],
        "USER": os.environ["RDS_USERNAME"],
        "PASSWORD": os.environ["RDS_PASSWORD"],
        "HOST": os.environ["RDS_HOSTNAME"],
        "PORT": os.environ["RDS_PORT"],
    },
}
SECRET_KEY = os.environ.get("SECRET_KEY")
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
STRIPE_API_KEY = os.environ.get("STRIP_API_KEY")
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET")

# JWT
GRAPHQL_JWT = {
    "JWT_VERIFY_EXPIRATION": True,
    "JWT_EXPIRATION_DELTA": timedelta(minutes=20),
    "JWT_CSRF_ROTATION": True,
}
