from rest_framework import serializers

from test_task.locations.models import Location, Category


class CategoryNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")


class LocationListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name")
    average_rating = serializers.FloatField(default=0)
    review_count = serializers.IntegerField(default=0)
    popularity_score = serializers.FloatField(default=0)

    class Meta:
        model = Location
        fields = (
            "id",
            "name",
            "category_name",
            "latitude",
            "longitude",
            "address",
            "is_active",
            "view_count",
            "average_rating",
            "review_count",
            "popularity_score",
        )
        read_only_fields = fields


class LocationRetrieveSerializer(serializers.ModelSerializer):
    category = CategoryNestedSerializer()
    average_rating = serializers.FloatField(default=0)
    review_count = serializers.IntegerField(default=0)
    popularity_score = serializers.FloatField(default=0)

    class Meta:
        model = Location
        fields = (
            "id",
            "name",
            "description",
            "category",
            "latitude",
            "longitude",
            "address",
            "is_active",
            "view_count",
            "average_rating",
            "review_count",
            "popularity_score",
        )
        read_only_fields = fields


class LocationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ("name", "description", "category", "latitude", "longitude", "address")


class LocationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ("name", "description", "category", "latitude", "longitude", "address")
        extra_fields = {
            "name": {"required": False},
            "description": {"required": False},
            "category": {"required": False},
            "latitude": {"required": False},
            "longitude": {"required": False},
            "address": {"required": False},
        }
