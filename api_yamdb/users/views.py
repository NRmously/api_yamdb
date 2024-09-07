from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .models import User
from .permissions import IsSuperUserOrIsAdmin
from .serializers import (UserCreateSerializer, UserRecieveTokenSerializer,
                          UserSerializer)
from .utils import send_confirmation_code


class UserCreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Вьюсет для создания новых пользователей.

    Разрешает доступ всем пользователям для регистрации.
    После успешного создания пользователя отправляет на его
    email код подтверждения.
    """

    permission_classes = (permissions.AllowAny,)
    serializer_class = UserCreateSerializer

    def create(self, request):
        """
        Обрабатывает запрос на создание пользователя.

        Если пользователь с таким же именем пользователя и email
        уже существует, обновляет его данные.
        В любом случае отправляет код подтверждения
        на email пользователя.

        Возвращает JSON-ответ с данными пользователя и статусом 200 (OK).
        """
        serializer = self.serializer_class(data=request.data)
        if User.objects.filter(
            username=request.data.get("username"),
            email=request.data.get("email")
        ):
            user = User.objects.get(username=request.data.get("username"))
            serializer = UserCreateSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        username = request.data.get("username")
        user = User.objects.get(username=username)
        confirmation_code = default_token_generator.make_token(user)
        send_confirmation_code(
            email=user.email, confirmation_code=confirmation_code
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserReceiveTokenViewSet(mixins.CreateModelMixin,
                              viewsets.GenericViewSet):
    """
    Вьюсет для получения JWT-токена по имени
    пользователя и коду подтверждения.

    Разрешает доступ всем пользователям.
    """

    queryset = User.objects.all()
    serializer_class = UserRecieveTokenSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        """
        Обрабатывает запрос на получение токена.

        Проверяет, соответствует ли код подтверждения пользователю.
        Если код неверен, возвращает ошибку 400 (Bad Request).
        Если код верен, возвращает JWT-токен и статус 200 (OK).
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get("username")
        confirmation_code = serializer.validated_data.get("confirmation_code")
        user = get_object_or_404(User, username=username)

        if not default_token_generator.check_token(user, confirmation_code):
            message = {"confirmation_code": "Неверный код подтверждения"}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        message = {"token": str(AccessToken.for_user(user))}
        return Response(message, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для управления пользователями.

    Доступен только администраторам и суперпользователям.
    Включает в себя операции просмотра, создания,
    обновления и удаления пользователей.
    Также предоставляет возможность частичного
    обновления данных текущего пользователя.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsSuperUserOrIsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)
    lookup_field = "username"

    def update(self, *args, **kwargs):
        """
        Запрещает использование метода POST для обновления пользователей.

        Вызывает исключение MethodNotAllowed с
        сообщением о необходимости использовать PATCH.
        """
        raise MethodNotAllowed("POST", detail="Use PATCH")

    def partial_update(self, *args, **kwargs):
        """
        Разрешает частичное обновление данных пользователя.

        Использует PATCH-запрос для обновления определённых полей.
        """
        return super().update(*args, **kwargs, partial=True)

    @action(
        detail=False,
        methods=["get", "patch"],
        url_path="me",
        url_name="me",
        permission_classes=(permissions.IsAuthenticated,),
    )
    def get_me_data(self, request):
        """
        Обрабатывает запросы GET и PATCH на URL /me/.

        GET-запрос возвращает данные текущего пользователя.
        PATCH-запрос обновляет данные текущего пользователя,
        но не изменяет его роль.
        Возвращает данные пользователя и статус 200 (OK).
        """
        if request.method == "PATCH":
            serializer = self.serializer_class(
                request.user,
                data=request.data,
                partial=True,
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
