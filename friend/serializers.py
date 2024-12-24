from rest_framework import serializers
from .models import FriendRequest, Friendship
from django.contrib.auth import get_user_model


User = get_user_model()

class FriendRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'status', 'created_at']

class FriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = ['user1', 'user2', 'created_at', 'chatroom_id']