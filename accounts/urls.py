from knox import views as knox_views
from .views import LoginAPI, RegisterAPI, FollowUserAPIView, UnfollowUserAPIView, UserProfileAPIView, \
    UserProfileUpdateAPIView
from django.urls import path



urlpatterns = [
    path('auth/register/', RegisterAPI.as_view(), name='register'),
    path('auth/login/', LoginAPI.as_view(), name='login'),
    path('auth/logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('auth/logoutall/', knox_views.LogoutAllView.as_view(), name='logoutall'),
    path('profile/<int:user_id>/', UserProfileAPIView.as_view(), name='user_profile'),
    path('profile/', UserProfileUpdateAPIView.as_view(), name='user_profile'),
    path('follow/<int:user_id>/', FollowUserAPIView.as_view(), name='follow_user'),
    path('unfollow/<int:user_id>/', UnfollowUserAPIView.as_view(), name='unfollow_user'),
]