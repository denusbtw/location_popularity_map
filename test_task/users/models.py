from django.contrib.auth.models import AbstractUser

from test_task.core.models import UUIDModel


class User(UUIDModel, AbstractUser):
    pass
