import dj_database_url

from .base import *

DEBUG = True

DATABASES = {
    "default": dj_database_url.parse(
        env("DEV_DATABASE_URL"),
    ),
}
