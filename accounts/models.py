from django.core.validators import EmailValidator
from django.db import models
from django.contrib.auth.models import AbstractUser

from django.contrib.auth import get_user_model


# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, validators=[EmailValidator(message='Email address must be unique.')])
    avatar = models.ImageField(upload_to='avatars', blank=True, null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        pass

User = get_user_model()
class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['follower', 'following']
