import pytest
from django.db import IntegrityError

from conftest import review_vote_factory
from test_task.reviews.models import Review


@pytest.mark.django_db
class TestReviewQuerySet:

    def test_annotate_upvote_count(self, review_factory, review_vote_factory):
        review = review_factory()
        upvotes = review_vote_factory.create_batch(2, upvote=True, review=review)
        downvotes = review_vote_factory.create_batch(3, downvote=True, review=review)

        review = Review.objects.annotate_upvote_count().get(pk=review.pk)
        assert review.upvote_count == len(upvotes)

    def test_annotate_downvote_count(self, review_factory, review_vote_factory):
        review = review_factory()
        upvotes = review_vote_factory.create_batch(2, upvote=True, review=review)
        downvotes = review_vote_factory.create_batch(3, downvote=True, review=review)

        review = Review.objects.annotate_downvote_count().get(pk=review.pk)
        assert review.upvote_count == len(downvotes)


@pytest.mark.django_db
class TestReviewModel:

    def test_error_if_location_and_user_not_unique(
        self, location_factory, user_factory, review_factory
    ):
        user = user_factory()
        location = location_factory()

        review_factory(user=user, location=location)
        with pytest.raises(IntegrityError):
            review_factory(user=user, location=location)

    def test_str(self, location_factory, review_factory, user_factory):
        user = user_factory(username="john")
        location = location_factory(name="metro")

        review = review_factory(user=user, location=location, rating=3)
        assert str(review) == "john - metro (3/5)"

        def __str__(self):
            return f"{self.user.username} - {self.location.name} ({self.rating}/{self.MAX_RATING})"


@pytest.mark.django_db
class TestReviewVoteModel:

    def test_error_if_review_and_user_not_unique(
        self, review_factory, user_factory, review_vote_factory
    ):
        review = review_factory()
        user = user_factory()

        review_vote_factory(review=review, user=user)
        with pytest.raises(IntegrityError):
            review_vote_factory(review=review, user=user)

    def test_str(self, review_factory, user_factory, review_vote_factory):
        review = review_factory(title="my review")
        user = user_factory(username="john")

        vote = review_vote_factory(review=review, user=user, upvote=True)
        assert str(vote) == "john Upvoted my review"
