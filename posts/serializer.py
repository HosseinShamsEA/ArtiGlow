import os
import requests
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from django.contrib.sites.shortcuts import get_current_site

from posts.models import Post, Comment, Like
from .image_resource import gen_image


class IsLikedField(serializers.RelatedField):
    def to_representation(self, value):
        return {'id': value.id, 'username': value.username}


class UserShortField(serializers.RelatedField):

    def to_representation(self, value):
        data = {'id': value.id, 'username': value.username}
        request = self.context.get('request')
        protocol = self.context.get('protocol', request.scheme if request else 'http')
        current_site = get_current_site(request)
        base_url = f"{protocol}://{current_site.domain}" if current_site else ''
        if value.avatar:
            data['avatar'] = base_url + value.avatar.url
        else:
            data['avatar'] = None
        return data


class LikeShortField(serializers.RelatedField):
    def to_representation(self, value):
        return {'owner_id': value.owner.id, 'created_at': value.created_at}


class LikeSerializer(serializers.ModelSerializer):
    owner = UserShortField(many=False, read_only=True)

    class Meta:
        model = Like
        fields = ('id', 'post', 'owner', 'created_at')
        read_only_fields = ('id', 'created_at')

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        like_obj = Like.objects.create(**validated_data)
        return like_obj


class PostSerializer(ModelSerializer):
    owner = UserShortField(many=False, read_only=True)
    likes = LikeShortField(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_followed = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id', 'description', 'owner', 'likes', 'is_followed', 'is_liked', 'likes_count', 'comments_count', 'image',
            'created_at',
            'updated_at',)
        read_only_fields = ['id', 'created_at', 'likes', 'image', 'likes_count', 'comments_count', 'updated_at']

    def get_is_liked(self, obj):
        user = self.context['request'].user
        likes = []
        for like in obj.likes.all():
            likes.append(like.owner.id)
        if user.is_authenticated and user.id in likes:
            return True
        return False

    def get_is_followed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated and obj.owner in user.following.all():
            return True
        return False

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['is_liked'] = self.get_is_liked(instance)
        representation['is_followed'] = self.get_is_followed(instance)
        return representation

    def create(self, validated_data):
        # set post owner
        validated_data['owner'] = self.context['request'].user

        try:
            # generate image from prompt
            image_url = gen_image(validated_data['description'])

            # download and save image temporarily
            r = requests.get(image_url)
            if r.status_code == 200:
                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(r.content)
                img_temp.flush()
            else:
                raise Exception(f'could not download image at {image_url}')

        except Exception as e:
            raise serializers.ValidationError(f"An error occurred while generating the image: {e}")

        # save post with image
        post_obj = Post.objects.create(**validated_data)
        post_obj.image.save(os.path.basename(image_url) + '.jpg', File(img_temp), save=True)

        return post_obj


class CommentSerializer(serializers.ModelSerializer):
    owner = UserShortField(many=False, read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'post', 'owner', 'description', 'created_at')
        read_only_fields = ('id', 'created_at', 'post', 'owner')
