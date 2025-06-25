import pytest
from rest_framework.test import APIClient

from test_task.locations.tests.factories import LocationFactory, CategoryFactory
from test_task.users.tests.factories import UserFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_factory():
    return UserFactory


@pytest.fixture
def category_factory():
    return CategoryFactory


@pytest.fixture
def location_factory():
    return LocationFactory
