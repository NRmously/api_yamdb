from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Review, Title
from users.models import User
from .filters import GenreCategorySlugFilter
from .mixins import CreateListDestroyViewSet
from .permissions import (IsAdminOrModeratorOrOwnerOrReadOnly,
                          IsAdminOrReadOnly, IsSuperUserOrIsAdmin)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleGetSerializer, TitleSerializer,
                          UserCreateSerializer, UserRecieveTokenSerializer,
                          UserSerializer)
from .utils import send_confirmation_code


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.order_by('id').annotate(
        rating=Avg('reviews__score')
    )
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_class = GenreCategorySlugFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleGetSerializer
        return TitleSerializer


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,
                          IsAdminOrModeratorOrOwnerOrReadOnly]
    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get("title_id"))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,
                          IsAdminOrModeratorOrOwnerOrReadOnly]
    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


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
        serializer.is_valid(raise_exception=True)
        user, _ = User.objects.get_or_create(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
        )
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
        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data.get('confirmation_code')
        user = get_object_or_404(User, username=username)

        if not default_token_generator.check_token(user, confirmation_code):
            message = {'confirmation_code': 'Неверный код подтверждения'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        message = {'token': str(AccessToken.for_user(user))}
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
    search_fields = ('username',)
    lookup_field = 'username'

    def update(self, *args, **kwargs):
        """
        Запрещает использование метода POST для обновления пользователей.

        Вызывает исключение MethodNotAllowed с
        сообщением о необходимости использовать PATCH.
        """
        raise MethodNotAllowed('POST', detail='Use PATCH')

    def partial_update(self, *args, **kwargs):
        """
        Разрешает частичное обновление данных пользователя.

        Использует PATCH-запрос для обновления определённых полей.
        """
        return super().update(*args, **kwargs, partial=True)

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        url_name='me',
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
        if request.method == 'PATCH':
            serializer = self.serializer_class(
                request.user,
                data=request.data,
                partial=True,
                context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
