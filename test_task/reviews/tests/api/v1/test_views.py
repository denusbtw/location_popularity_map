import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from test_task.reviews.models import Review, ReviewVote


@pytest.fixture
def location(location_factory):
    return location_factory(is_active=True)


@pytest.fixture
def review_list_url(location):
    return reverse("v1:review_list", kwargs={"location_id": location.pk})


@pytest.fixture
def review(location, review_factory):
    return review_factory(location=location)


@pytest.fixture
def review_detail_url(review):
    return reverse(
        "v1:review_detail", kwargs={"location_id": review.location_id, "pk": review.pk}
    )


@pytest.fixture
def review_vote_create_url(review):
    return reverse("v1:review_vote_create", kwargs={"review_id": review.pk})


@pytest.fixture
def review_upvote(review, review_vote_factory):
    return review_vote_factory(review=review, upvote=True)


@pytest.fixture
def review_downvote(review, review_vote_factory):
    return review_vote_factory(review=review, downvote=True)


@pytest.fixture
def review_vote_detail_url(review_upvote):
    return reverse(
        "v1:review_vote_detail",
        kwargs={"review_id": review_upvote.review_id, "pk": review_upvote.pk},
    )


@pytest.mark.django_db
class TestReviewListCreateAPIView:

    @pytest.mark.parametrize(
        "method, expected_status_code",
        [
            ("get", status.HTTP_200_OK),
            ("post", status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_anonymous_user(
        self, api_client, review_list_url, method, expected_status_code
    ):
        response = getattr(api_client, method)(review_list_url)
        assert response.status_code == expected_status_code

    @pytest.mark.parametrize(
        "method, expected_status_code",
        [
            ("get", status.HTTP_200_OK),
            ("post", status.HTTP_201_CREATED),
        ],
    )
    def test_authenticated_user(
        self, api_client, review_list_url, user_factory, method, expected_status_code
    ):
        user = user_factory()
        api_client.force_authenticate(user=user)

        data = {"title": "test title", "body": "test body", "rating": 3}
        response = getattr(api_client, method)(review_list_url, data)
        assert response.status_code == expected_status_code

    def test_perform_create(self, api_client, review_list_url, user_factory, location):
        user = user_factory()
        api_client.force_authenticate(user=user)

        data = {"title": "test title", "body": "test body", "rating": 3}
        response = api_client.post(review_list_url, data)
        assert response.status_code == status.HTTP_201_CREATED

        review = Review.objects.get(id=response.data["id"])
        assert review.user_id == user.pk
        assert review.location_id == location.pk

    def test_lists_reviews_only_of_specified_location(
        self, api_client, review_list_url, location, review_factory
    ):
        expected_review = review_factory(location=location)
        review_factory()

        response = api_client.get(review_list_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == str(expected_review.id)


@pytest.mark.django_db
class TestReviewDetailAPIview:

    @pytest.mark.parametrize(
        "method, expected_status_code",
        [
            ("get", status.HTTP_200_OK),
            ("put", status.HTTP_403_FORBIDDEN),
            ("patch", status.HTTP_403_FORBIDDEN),
            ("delete", status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_anonymous_user(
        self, api_client, review_detail_url, method, expected_status_code
    ):
        response = getattr(api_client, method)(review_detail_url)
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
    def test_not_review_user(
        self, api_client, review_detail_url, user_factory, method, expected_status_code
    ):
        user = user_factory()
        api_client.force_authenticate(user=user)

        response = getattr(api_client, method)(review_detail_url)
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
    def test_review_user(
        self, api_client, review_detail_url, review, method, expected_status_code
    ):
        api_client.force_authenticate(user=review.user)
        response = getattr(api_client, method)(review_detail_url)
        assert response.status_code == expected_status_code


@pytest.mark.django_db
class TestReviewVoteCreateAPIView:

    @pytest.mark.parametrize(
        "method, expected_status_code",
        [
            ("get", status.HTTP_403_FORBIDDEN),
            ("post", status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_anonymous_user(
        self, api_client, review_vote_create_url, method, expected_status_code
    ):
        response = getattr(api_client, method)(review_vote_create_url)
        assert response.status_code == expected_status_code

    @pytest.mark.parametrize(
        "method, expected_status_code",
        [
            ("get", status.HTTP_405_METHOD_NOT_ALLOWED),
            ("post", status.HTTP_201_CREATED),
        ],
    )
    def test_authenticated_user(
        self,
        api_client,
        review_vote_create_url,
        user_factory,
        method,
        expected_status_code,
    ):
        user = user_factory()
        api_client.force_authenticate(user=user)

        data = {"vote": ReviewVote.Vote.UPVOTE}
        response = getattr(api_client, method)(review_vote_create_url, data)
        assert response.status_code == expected_status_code

    def test_perform_create(
        self, api_client, review_vote_create_url, user_factory, review
    ):
        user = user_factory()
        api_client.force_authenticate(user=user)

        data = {"vote": ReviewVote.Vote.UPVOTE}
        response = api_client.post(review_vote_create_url, data)
        assert response.status_code == status.HTTP_201_CREATED

        review_vote = ReviewVote.objects.get(id=response.data["id"])
        assert review_vote.user_id == user.id
        assert review_vote.review_id == review.id


@pytest.mark.django_db
class TestReviewVoteDetailAPIView:

    @pytest.mark.parametrize(
        "method, expected_status_code",
        [
            ("get", status.HTTP_403_FORBIDDEN),
            ("put", status.HTTP_403_FORBIDDEN),
            ("patch", status.HTTP_403_FORBIDDEN),
            ("delete", status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_anonymous_user(
        self, api_client, review_vote_detail_url, method, expected_status_code
    ):
        response = getattr(api_client, method)(review_vote_detail_url)
        assert response.status_code == expected_status_code

    @pytest.mark.parametrize(
        "method, expected_status_code",
        [
            ("get", status.HTTP_404_NOT_FOUND),
            ("put", status.HTTP_404_NOT_FOUND),
            ("patch", status.HTTP_404_NOT_FOUND),
            ("delete", status.HTTP_404_NOT_FOUND),
        ],
    )
    def test_not_review_vote_user(
        self,
        api_client,
        review_vote_detail_url,
        user_factory,
        method,
        expected_status_code,
    ):
        user = user_factory()
        api_client.force_authenticate(user=user)

        response = getattr(api_client, method)(review_vote_detail_url)
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
    def test_review_vote_user(
        self,
        api_client,
        review_vote_detail_url,
        review_upvote,
        method,
        expected_status_code,
    ):
        api_client.force_authenticate(user=review_upvote.user)

        data = {"vote": ReviewVote.Vote.DOWNVOTE}
        response = getattr(api_client, method)(review_vote_detail_url, data)
        assert response.status_code == expected_status_code
