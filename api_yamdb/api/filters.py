from django_filters import CharFilter
from django_filters.rest_framework import FilterSet

from reviews.models import Title


class GenreCategorySlugFilter(FilterSet):
    genre = CharFilter(field_name='genre__slug')
    category = CharFilter(field_name='category__slug')

    class Meta:
        model = Title
        fields = ['name', 'year', 'category', 'genre']
