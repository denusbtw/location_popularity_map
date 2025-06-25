from django_filters import rest_framework as filters

from test_task.locations.models import Location


class LocationFilterSet(filters.FilterSet):
    category_name = filters.CharFilter(
        field_name="category__name", lookup_expr="icontains"
    )
    average_rating_min = filters.NumberFilter(
        field_name="average_rating", lookup_expr="gte"
    )
    average_rating_max = filters.NumberFilter(
        field_name="average_rating", lookup_expr="lte"
    )

    class Meta:
        model = Location
        fields = (
            "category",
            "category_name",
            "average_rating_min",
            "average_rating_max",
        )
