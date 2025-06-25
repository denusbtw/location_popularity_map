from rest_framework import serializers

from test_task.reviews.models import Review, ReviewVote
from test_task.users.api.v1.serializers import UserNestedSerializer


class ReviewListSerializer(serializers.ModelSerializer):
    user = UserNestedSerializer()
    upvote_count = serializers.IntegerField(default=0)
    downvote_count = serializers.IntegerField(default=0)

    class Meta:
        model = Review
        fields = (
            "id",
            "user",
            "title",
            "body",
            "rating",
            "upvote_count",
            "downvote_count",
        )
        read_only_fields = fields


class ReviewRetrieveSerializer(serializers.ModelSerializer):
    user = UserNestedSerializer()
    upvote_count = serializers.IntegerField(default=0)
    downvote_count = serializers.IntegerField(default=0)

    class Meta:
        model = Review
        fields = (
            "id",
            "user",
            "title",
            "body",
            "rating",
            "upvote_count",
            "downvote_count",
        )
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


class ReviewVoteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewVote
        fields = ("vote",)


class ReviewVoteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewVote
        fields = ("vote",)
