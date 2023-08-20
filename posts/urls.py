from django.urls import path
from .views import PostViewSet, CommentViewSet
from django.urls import path, include
# from rest_framework import routers
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register(r'posts', PostViewSet, basename="post")
post_comments_router = routers.NestedDefaultRouter(router, r'posts', lookup='post')
post_comments_router.register(r'comments', CommentViewSet, basename='post-comments')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(post_comments_router.urls)),
]
