from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitleViewSet, UserCreateViewSet,
                    UserReceiveTokenViewSet, UserViewSet)

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register('users', UserViewSet, basename='users')
router_v1.register('titles', TitleViewSet, basename='Title')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

auth_urls_v1 = [
    path(
        'signup/',
        UserCreateViewSet.as_view({'post': 'create'}),
        name='signup'
    ),
    path(
        'token/',
        UserReceiveTokenViewSet.as_view({'post': 'create'}),
        name='token'
    ),
]

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include(auth_urls_v1)),
]
