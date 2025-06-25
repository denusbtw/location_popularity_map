from django.core.validators import (
    MaxValueValidator,
    MaxLengthValidator,
    MinValueValidator,
)
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, IntegerField

from test_task.core.models import UUIDModel, TimestampedModel
from test_task.locations.models import Location

User = get_user_model()


class ReviewQuerySet(models.QuerySet):

    def annotate_upvote_count(self):
        return self.annotate(
            upvote_count=Count(
                "votes",
                Q(votes__vote=ReviewVote.Vote.UPVOTE),
                output_field=IntegerField(),
            )
        )

    def annotate_downvote_count(self):
        return self.annotate(
            upvote_count=Count(
                "votes",
                Q(votes__vote=ReviewVote.Vote.DOWNVOTE),
                output_field=IntegerField(),
            )
        )


class Review(UUIDModel, TimestampedModel):
    MIN_RATING = 1
    MAX_RATING = 5

    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    title = models.CharField(max_length=255)
    body = models.TextField(validators=[MaxLengthValidator(2000)])
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN_RATING),
            MaxValueValidator(MAX_RATING),
        ]
    )

    objects = ReviewQuerySet.as_manager()

    class Meta:
        unique_together = ("location", "user")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=("location",)),
            models.Index(fields=("title",)),
            models.Index(fields=("body",)),
            models.Index(fields=("rating",)),
            models.Index(fields=("created_at",)),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.location.name} ({self.rating}/{self.MAX_RATING})"


class ReviewVote(UUIDModel, TimestampedModel):
    class Vote(models.IntegerChoices):
        UPVOTE = 1, "Upvote"
        DOWNVOTE = -1, "Downvote"

    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="votes")
    vote = models.SmallIntegerField(choices=Vote.choices)

    class Meta:
        unique_together = ("review", "user")
        indexes = [
            models.Index(fields=("user", "review_id")),
            models.Index(fields=("vote",)),
        ]

    def __str__(self):
        vote_display = self.get_vote_display()
        return f"{self.user.username} {vote_display}d {self.review.title}"
