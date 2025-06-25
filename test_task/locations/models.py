from django.core.validators import (
    MaxLengthValidator,
    MinValueValidator,
    MaxValueValidator,
)
from django.db import models

from test_task.core.models import UUIDModel, TimestampedModel


class Category(UUIDModel, TimestampedModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


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

    class Meta:
        unique_together = ("latitude", "longitude")
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
