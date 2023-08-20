from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status

from posts.models import Post, Like
from django.contrib.auth import get_user_model


class LikeTests(APITestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.client.force_authenticate(user=self.user)
        self.post = Post.objects.create(description='Test post', owner=self.user)

    def test_like_post(self):
        url = f'/posts/{self.post.pk}/like/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Post liked successfully.')

        self.post.refresh_from_db()
        self.assertEqual(self.post.likes_count, 1)


    def test_unlike_post(self):
        Like.objects.create(owner=self.user, post=self.post)
        self.post.likes_count += 1
        self.post.save()
        url = f'/posts/{self.post.pk}/like/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['message'], 'Post unliked successfully.')

        self.post.refresh_from_db()
        self.assertEqual(self.post.likes_count, 0)
