import datetime as dt
from rest_framework import serializers

from reviews.models import Category, Genre, Title


class TitleSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Title

    def validate_year(self, value):
        if not (value < dt.date.today().year):
            raise serializers.ValidationError('Проверьте год выпуска')
        return value


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Genre
