import pytest

from test_task.users.tests.factories import UserFactory


@pytest.fixture
def user_factory():
    return UserFactory
