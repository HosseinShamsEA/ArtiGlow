from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response

from .models import Post, Comment, Like
from posts.serializer import PostSerializer, CommentSerializer
from rest_framework.decorators import action

from rest_framework import filters

from .permissions import IsCommentOwnerOrReadOnly


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['description']
    filterset_fields = ['owner']

    def get_queryset(self):
        user = self.request.user
        if self.request.user.is_superuser:
            return Post.objects.all()
        else:
            request_type = self.request.method
            if request_type == 'DELETE':
                return Post.objects.filter(owner=user)
            elif request_type == "GET":
                return Post.objects.prefetch_related("likes").all()
            else:
                return Post.objects.none

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):

        post = Post.objects.filter(id=pk).first()

        like = post.likes.filter(owner=request.user).first()
        if like is None:
            like = Like(owner=request.user, post=post)
            like.save()
            post.likes_count += 1
            post.save()
            return Response({'message': 'Post liked successfully.'}, status=status.HTTP_201_CREATED)

        like.delete()
        post.likes_count -= 1
        post.save()
        return Response({'message': 'Post unliked successfully.'}, status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsCommentOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user, post_id=self.kwargs['post_pk'])

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['post_pk'])
