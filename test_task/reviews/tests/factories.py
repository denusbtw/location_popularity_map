import factory

from test_task.locations.tests.factories import LocationFactory
from test_task.reviews.models import Review, ReviewVote
from test_task.users.tests.factories import UserFactory


class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Review

    location = factory.SubFactory(LocationFactory)
    user = factory.SubFactory(UserFactory)
    title = factory.Faker("sentence", nb_words=3)
    body = factory.Faker("paragraph", nb_sentences=3)
    rating = factory.Faker(
        "pyint", min_value=Review.MIN_RATING, max_value=Review.MAX_RATING
    )


class ReviewVoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReviewVote

    review = factory.SubFactory(ReviewFactory)
    user = factory.SubFactory(UserFactory)
    vote = factory.Faker(
        "random_element", elements=[c[0] for c in ReviewVote.Vote.choices]
    )

    class Params:
        upvote = factory.Trait(vote=ReviewVote.Vote.UPVOTE)
        downvote = factory.Trait(vote=ReviewVote.Vote.DOWNVOTE)
