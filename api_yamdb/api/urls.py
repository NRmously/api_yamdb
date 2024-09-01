from rest_framework.routers import DefaultRouter

from api.views import ReviewViewSet, CommentViewSet

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register(r'titles/(?P<id>\d+)/reviews', ReviewViewSet,
                   basename='review')
router_v1.register(r'titles/(?P<id>\d+)/reviews/(?P<id>\d+)/comments',
                   CommentViewSet, basename='comment')
