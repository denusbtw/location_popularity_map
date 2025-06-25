from django.core.validators import MaxValueValidator, MaxLengthValidator
from django.db import models
from django.contrib.auth import get_user_model

from test_task.core.models import UUIDModel, TimestampedModel
from test_task.locations.models import Location

User = get_user_model()


class Review(UUIDModel, TimestampedModel):
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
        validators=[MaxValueValidator(MAX_RATING)]
    )

    class Meta:
        unique_together = ("location", "user")
        ordering = ["-created_at"]

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

    def __str__(self):
        vote_display = self.get_vote_display()
        return f"{self.user.username} {vote_display}d {self.review.title}"
