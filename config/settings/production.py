import dj_database_url

from .base import *

DEBUG = False

DATABASES = {
    "default": dj_database_url.parse(
        env("PROD_DATABASE_URL"),
    ),
}

ALLOWED_HOSTS = []
