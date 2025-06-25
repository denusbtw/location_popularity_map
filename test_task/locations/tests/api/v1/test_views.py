import pytest
from rest_framework import status
from rest_framework.reverse import reverse


@pytest.fixture
def list_url():
    return reverse("v1:location_list")


@pytest.fixture
def location(location_factory):
    return location_factory(is_active=True)


@pytest.fixture
def detail_url(location):
    return reverse("v1:location_detail", kwargs={"pk": location.pk})


@pytest.mark.django_db
class TestLocationListCreateAPIView:

    @pytest.mark.parametrize(
        "method, expected_status_code",
        [
            ("get", status.HTTP_200_OK),
            ("post", status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_anonymous_user(self, api_client, list_url, method, expected_status_code):
        response = getattr(api_client, method)(list_url)
        assert response.status_code == expected_status_code

    @pytest.mark.parametrize(
        "method, expected_status_code",
        [
            ("get", status.HTTP_200_OK),
            ("post", status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_authenticated_user(
        self, api_client, list_url, user_factory, method, expected_status_code
    ):
        user = user_factory()
        api_client.force_authenticate(user=user)

        response = getattr(api_client, method)(list_url)
        assert response.status_code == expected_status_code

    @pytest.mark.parametrize(
        "method, expected_status_code",
        [
            ("get", status.HTTP_200_OK),
            ("post", status.HTTP_201_CREATED),
        ],
    )
    def test_admin_user(
        self,
        api_client,
        list_url,
        user_factory,
        category_factory,
        method,
        expected_status_code,
    ):
        admin = user_factory(is_staff=True)
        api_client.force_authenticate(user=admin)

        category = category_factory()

        data = {
            "name": "test location",
            "description": "test description",
            "category": category.pk,
            "latitude": 45,
            "longitude": 60,
            "address": "test address",
        }

        response = getattr(api_client, method)(list_url, data)
        assert response.status_code == expected_status_code

    def test_admin_sees_all_locations(
        self, api_client, list_url, location_factory, user_factory
    ):
        admin = user_factory(is_staff=True)
        api_client.force_authenticate(user=admin)

        location_factory(is_active=True)
        location_factory(is_active=False)

        response = api_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2

    def test_user_sees_only_active_locations(
        self, api_client, list_url, location_factory, user_factory
    ):
        user = user_factory()
        api_client.force_authenticate(user=user)

        active_loc = location_factory(is_active=True)
        inactive_loc = location_factory(is_active=False)

        response = api_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == str(active_loc.id)

    def test_search_by_name(self, api_client, list_url, location_factory):
        abc_loc = location_factory(name="abc", is_active=True)
        zxc_loc = location_factory(name="zxc", is_active=True)

        response = api_client.get(list_url, {"search": "xc"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        print(response.data["results"][0]["id"])
        assert response.data["results"][0]["id"] == str(zxc_loc.id)

    def test_filter_by_category_name(
        self, api_client, list_url, location_factory, category_factory
    ):
        abc_cat = category_factory(name="abc")
        zxc_cat = category_factory(name="zxc")

        abc_loc = location_factory(category=abc_cat, is_active=True)
        zxc_loc = location_factory(category=zxc_cat, is_active=True)

        response = api_client.get(list_url, {"category_name": "xc"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == str(zxc_loc.id)

    def test_order_by_view_count_desc(self, api_client, list_url, location_factory):
        loc_10_views = location_factory(view_count=10, is_active=True)
        loc_20_views = location_factory(view_count=20, is_active=True)

        response = api_client.get(list_url, {"ordering": "-view_count"})
        assert response.status_code == status.HTTP_200_OK
        actual_ids = [loc["id"] for loc in response.data["results"]]
        assert actual_ids == [str(loc_20_views.id), str(loc_10_views.id)]


@pytest.mark.django_db
class TestLocationDetailAPIView:

    @pytest.mark.parametrize(
        "method, expected_status_code",
        [
            ("get", status.HTTP_200_OK),
            ("put", status.HTTP_403_FORBIDDEN),
            ("patch", status.HTTP_403_FORBIDDEN),
            ("delete", status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_anonymous_user(self, api_client, detail_url, method, expected_status_code):
        response = getattr(api_client, method)(detail_url)
        assert response.status_code == expected_status_code

    @pytest.mark.parametrize(
        "method, expected_status_code",
        [
            ("get", status.HTTP_200_OK),
            ("put", status.HTTP_403_FORBIDDEN),
            ("patch", status.HTTP_403_FORBIDDEN),
            ("delete", status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_authenticated_user(
        self, api_client, detail_url, user_factory, method, expected_status_code
    ):
        user = user_factory()
        api_client.force_authenticate(user=user)

        response = getattr(api_client, method)(detail_url)
        assert response.status_code == expected_status_code

    @pytest.mark.parametrize(
        "method, expected_status_code",
        [
            ("get", status.HTTP_200_OK),
            ("put", status.HTTP_200_OK),
            ("patch", status.HTTP_200_OK),
            ("delete", status.HTTP_204_NO_CONTENT),
        ],
    )
    def test_admin_user(
        self,
        api_client,
        detail_url,
        user_factory,
        category_factory,
        method,
        expected_status_code,
    ):
        admin = user_factory(is_staff=True)
        api_client.force_authenticate(user=admin)

        category = category_factory()

        data = {
            "name": "test location",
            "description": "test description",
            "category": category.pk,
            "latitude": 45,
            "longitude": 60,
            "address": "test address",
        }

        response = getattr(api_client, method)(detail_url, data)
        assert response.status_code == expected_status_code

    def test_view_count_is_incremented_after_response(
        self, api_client, detail_url, location
    ):
        response = api_client.get(detail_url)
        assert response.status_code == status.HTTP_200_OK

        old_view_count = location.view_count

        location.refresh_from_db()
        assert location.view_count == (old_view_count + 1)

    def test_delete_deactivates_location(
        self, api_client, user_factory, detail_url, location
    ):
        admin = user_factory(is_staff=True)
        api_client.force_authenticate(user=admin)

        response = api_client.delete(detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        location.refresh_from_db()
        assert location.is_active is False
