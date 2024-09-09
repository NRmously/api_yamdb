from django.utils import timezone
from rest_framework import serializers

from api_yamdb.settings import FORBIDDEN_SYMBOL
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        exclude = ('id',)
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
        title = self.context['view'].kwargs.get('title_id')
        author = self.context['request'].user
        if (
            request.method == 'POST' and Review.objects.filter(
                title=title, author=author).exists()):
            raise serializers.ValidationError(
                'Ваш отзыв на это произведение уже опубликован')
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

    username = serializers.RegexField(r'^[\w.@+-]+\Z', max_length=150)
    email = serializers.EmailField(max_length=254)

    def validate(self, data):
        """Проверка уже зарегестрированных пользователей."""
        email_exists = User.objects.filter(email=data.get('email')).exists()
        username_exists = User.objects.filter(
            username=data.get('username')
        ).exists()
        if email_exists and not username_exists:
            raise serializers.ValidationError(
                'Пользователь с этой почтой уже существует!'
            )
        if username_exists and not email_exists:
            raise serializers.ValidationError(
                'Пользователь с таким логином уже существует!'
            )
        return data

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
