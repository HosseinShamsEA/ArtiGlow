from rest_framework import generics, permissions, viewsets, status
from rest_framework.authtoken.admin import User
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from knox.models import AuthToken
from rest_framework.views import APIView

from .models import Follow
from .serializers import UserSerializer, RegisterSerializer, FollowSerializer, UserProfileSerializer, \
    UserProfileUpdateSerializer
from django.contrib.auth import login
from rest_framework import permissions
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.views import LoginView as KnoxLoginView


# Register API
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)

        try:
            user_profile = User.objects.get(pk=user.id)
        except User.DoesNotExist:
            response = super(LoginAPI, self).post(request, format=None)
            response.data['user'] = UserSerializer(user).data
            return response

        response = super(LoginAPI, self).post(request, format=None)
        response.data['user'] = UserProfileSerializer(user_profile, context={"request": request}).data
        return response


class FollowUserAPIView(APIView):
    def post(self, request, user_id):
        user_to_follow = User.objects.get(pk=user_id)
        if request.user != user_to_follow:
            follow, created = Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
            if created:
                serializer = FollowSerializer(follow)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'You are already following this user.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)


class UnfollowUserAPIView(APIView):
    def delete(self, request, user_id):
        user_to_unfollow = User.objects.get(pk=user_id)
        follow = Follow.objects.filter(follower=request.user, following=user_to_unfollow).first()
        if follow:
            follow.delete()
            return Response({'message': 'You have unfollowed this user.'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'You are not following this user.'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileAPIView(APIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
            serializer = UserProfileSerializer(user, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)


class UserProfileUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request):
        serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
