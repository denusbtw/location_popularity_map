from rest_framework import serializers

from test_task.reviews.models import Review
from test_task.users.api.v1.serializers import UserNestedSerializer


class ReviewListSerializer(serializers.ModelSerializer):
    user = UserNestedSerializer()

    class Meta:
        model = Review
        fields = ("id", "user", "title", "body", "rating")
        read_only_fields = fields


class ReviewRetrieveSerializer(serializers.ModelSerializer):
    user = UserNestedSerializer()

    class Meta:
        model = Review
        fields = ("id", "user", "title", "body", "rating")
        read_only_fields = fields


class ReviewCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = ("title", "body", "rating")


class ReviewUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = ("title", "body", "rating")
        extra_kwargs = {
            "title": {"required": False},
            "body": {"required": False},
            "rating": {"required": False},
        }
