import datetime as dt
from rest_framework import serializers

from reviews.models import Category, Genre, Title, GenreTitle


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Category
        lookup_field = 'slug'

class TitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field='slug', queryset=Category.objects.all())
    genre = serializers.SlugRelatedField(many=True, slug_field='slug', queryset=Genre.objects.all())

    class Meta:
        fields = ('id', 'name', 'year', 'category', 'genre', 'description')
        model = Title

    def validate_year(self, value):
        if not (value < dt.date.today().year):
            raise serializers.ValidationError('Проверьте год выпуска')
        return value


class TitleGetSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)

    class Meta:
        fields = ('id', 'name', 'year', 'category', 'genre', 'description')
        model = Title
