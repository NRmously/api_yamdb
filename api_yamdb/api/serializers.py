from django.utils import timezone
from rest_framework import serializers

from api_yamdb.settings import FORBIDDEN_SYMBOL
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


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
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )

    class Meta:
        fields = ('id', 'name', 'year', 'category', 'genre', 'description')
        model = Title

    def validate_year(self, value):
        if not value < timezone.now().year:
            raise serializers.ValidationError('Проверьте год выпуска')
        return value


class TitleGetSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'category',
            'rating',
            'genre',
            'description'
        )
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    def validate(self, data):
        request = self.context.get('request')
        if request.method == 'POST':
            review = Review.objects.filter(
                title=self.context['view'].kwargs.get('title_id'),
                author=self.context['request'].user
            )
            if review.exists():
                raise serializers.ValidationError(
                    'Ваш отзыв на это произведение уже опубликован'
                )
        return data

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'comments')
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )
    review = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date', 'review')
        model = Comment


class BaseUser(serializers.ModelSerializer):
    """Базовый класс сериализатора с валидацией для поля username."""

    def validate_username(self, data):
        if data == 'me' or data == 'admin':
            raise serializers.ValidationError("Использовать это имя запрещено")
        return data


class UserCreateSerializer(BaseUser):
    """
    Сериализатор для создания пользователей,
    работающий только с полями username и email.
    """

    class Meta:
        model = User
        fields = ('username', 'email')


class UserRecieveTokenSerializer(serializers.Serializer):
    """
    Сериализатор для получения токена,
    работающий с полями username и confirmation_code.
    """

    username = serializers.RegexField(
        regex=FORBIDDEN_SYMBOL, max_length=150, required=True
    )
    confirmation_code = serializers.CharField(max_length=150, required=True)


class UserSerializer(BaseUser):
    """
    Основной сериализатор для работы с пользователями,
    включающий все ключевые поля модели User.
    """

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
