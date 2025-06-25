from django.core.validators import (
    MaxLengthValidator,
    MinValueValidator,
    MaxValueValidator,
)
from django.db import models
from django.db.models import Avg, Count, F
from django.db.models.fields import FloatField
from django.db.models.functions import Coalesce

from test_task.core.models import UUIDModel, TimestampedModel


class Category(UUIDModel, TimestampedModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class LocationQuerySet(models.QuerySet):

    def annotate_average_rating(self):
        return self.annotate(
            average_rating=Coalesce(
                Avg("reviews__rating"), 0, output_field=FloatField()
            )
        )

    def annotate_review_count(self):
        return self.annotate(review_count=Count("reviews"))

    def annotate_popularity_score(self):
        rating_weight = 0.6
        reviews_weight = 0.3
        views_weight = 0.1

        return self.annotate(
            popularity_score=Coalesce(
                (
                    F("average_rating") * rating_weight
                    + F("review_count") * reviews_weight
                    + F("view_count") * views_weight
                ),
                0,
                output_field=FloatField(),
            )
        )


class Location(UUIDModel, TimestampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(validators=[MaxLengthValidator(5000)])
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="locations",
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )
    address = models.CharField(max_length=255, unique=True)

    is_active = models.BooleanField(default=True)
    view_count = models.PositiveBigIntegerField(default=0)

    objects = LocationQuerySet.as_manager()

    class Meta:
        unique_together = ("latitude", "longitude")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=("is_active",)),
            models.Index(fields=("view_count",)),
            models.Index(fields=("created_at",)),
            models.Index(fields=["name"]),
            models.Index(fields=["description"]),
        ]

    def __str__(self):
        return self.name
