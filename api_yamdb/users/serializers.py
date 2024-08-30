from rest_framework import serializers

from .models import User
from api_yamdb.settings import FORBIDDEN_SYMBOL


class BaseUser(serializers.ModelSerializer):
    """Базовый класс сериализатора с валидацией для поля username."""

    def validate_username(self, data):
        if self.initial_data.get('username') == ('me' or 'admin'):
            raise serializers.ValidationError("Использовать это имя запрещено")
        return data


class UserCreateSerializer(BaseUser):
    """
    Сериализатор для создания пользователей,
    работающий только с полями username и email.
    """

    class Meta:
        model = User
        fields = ("username", "email")


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
            "username", "email", "first_name", "last_name", "bio", "role"
        )
