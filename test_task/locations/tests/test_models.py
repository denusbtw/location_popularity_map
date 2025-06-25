import pytest
from django.db import IntegrityError

from test_task.locations.models import Location


@pytest.mark.django_db
class TestCategoryModel:

    def test_str(self, category_factory):
        category = category_factory(name="abc")
        assert str(category) == "abc"


@pytest.mark.django_db
class TestLocationQuerySet:

    def test_annotate_average_rating(self, location_factory, review_factory):
        location = location_factory()

        review_1_star = review_factory(rating=1, location=location)
        review_3_star = review_factory(rating=3, location=location)

        location = Location.objects.annotate_average_rating().get(pk=location.pk)

        expected_average_rating = (review_1_star.rating + review_3_star.rating) / 2
        assert location.average_rating == expected_average_rating

    def test_annotate_popularity_score(self, location_factory, review_factory):
        location = location_factory(view_count=1)
        review = review_factory(rating=3, location=location)

        location = (
            Location.objects.annotate_average_rating()
            .annotate_review_count()
            .annotate_popularity_score()
            .get(pk=location.pk)
        )

        expected_popularity_score = round(0.6 * 3 + 0.3 * 1 + 0.1 * 1, 2)
        assert location.popularity_score == expected_popularity_score

    def test_annotate_review_count(self, location_factory, review_factory):
        location = location_factory()
        review_locations = review_factory.create_batch(2, location=location)
        review_factory.create_batch(3)

        location = Location.objects.annotate_review_count().get(pk=location.pk)
        assert location.review_count == len(review_locations)


@pytest.mark.django_db
class TestLocationModel:

    def test_error_if_latitude_and_longitude_not_unique(self, location_factory):
        latitude = 50
        longitude = 50

        location_factory(latitude=latitude, longitude=longitude)
        with pytest.raises(IntegrityError):
            location_factory(latitude=latitude, longitude=longitude)

    def test_str(self, location_factory):
        location = location_factory(name="abc")
        assert str(location) == "abc"
