from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, GenreViewSet, TitleViewSet
from users.views import UserCreateViewSet, UserReceiveTokenViewSet, UserViewSet

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register("users", UserViewSet, basename="users")
router_v1.register('titles', TitleViewSet)#, basename='Title')
router_v1.register('categories', CategoryViewSet)
router_v1.register('genres', GenreViewSet)

auth_urls_v1 = [
    path(
        "signup/",
        UserCreateViewSet.as_view({"post": "create"}),
        name="signup"
    ),
    path(
        "token/",
        UserReceiveTokenViewSet.as_view({"post": "create"}),
        name="token"
    ),
]

urlpatterns = [
    path('', include(router_v1.urls)),
    path("auth/", include(auth_urls_v1)),
]
