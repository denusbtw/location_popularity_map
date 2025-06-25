import factory

from test_task.locations.models import Category, Location


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"Category {n+1}")


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Location

    name = factory.Faker("company")
    description = factory.Faker("paragraph", nb_sentences=3)
    category = factory.SubFactory(CategoryFactory)

    latitude = factory.Faker("pydecimal", min_value=-90, max_value=90, right_digits=6)
    longitude = factory.Faker(
        "pydecimal", min_value=-180, max_value=180, right_digits=6
    )
    address = factory.Faker("address")

    is_active = factory.Faker("boolean")
    view_count = factory.Faker("pyint", min_value=0, max_value=1000)
