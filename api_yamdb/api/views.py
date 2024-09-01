from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from reviews.models import Review, Title
from api_yamdb.api.serializers import ReviewSerializer, CommentSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly)

    def get_permissions(self):
        return super().get_permissions()

    def get_queryset(self, request, *args, **kwargs):
        title = get_object_or_404(Title, id=self.kwargs['id'])
        review = Review.objects.filter(author=self.request.user, title=title)
        if review.exists():
            content = {
                "Error : На данное произведение вы уже оставляли отзыв"
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs['id'])
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_permissions(self):
        return super().get_permissions()

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs['id'])
        queryset = review.comments.all()
        return queryset

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs['id'])
        serializer.save(author=self.request.user, review=review)
