import asyncio
from .models import FriendRequest, Friendship
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError, NotFound
from django.db.models import Q
from config.services import get_chatroom
from channels.layers import get_channel_layer
from user_management.redis_utils import get_channel_name
from user_management.services import UserService


User = get_user_model()

# 친구 요청 전송
async def send_friend_request(from_user_id, to_user_id):
    try:
        from_user = await User.objects.aget(id=from_user_id)
        to_user = await User.objects.aget(id=to_user_id)
    except User.DoesNotExist:
        raise NotFound("User not found.")

    if from_user == to_user:
        raise ValidationError("You cannot send a friend request to yourself.")

    if await FriendRequest.objects.filter(Q(from_user=from_user, to_user=to_user) | Q(from_user=to_user, to_user=from_user)).aexists():
        raise ValidationError("Friend request already exists or received.")

    if await Friendship.objects.filter(Q(user1=from_user, user2=to_user) | Q(user1=to_user, user2=from_user)).aexists():
        raise ValidationError("You are already friends.")

    friend_request = await FriendRequest.objects.acreate(from_user=from_user, to_user=to_user, status="pending")
    await send_friend_request_notification(from_user_id, to_user_id, friend_request.created_at)


# 친구 요청 알림 전송
async def send_friend_request_notification(from_user_id, to_user_id, created_at):
    channel_layer = get_channel_layer()
    channel_name = await get_channel_name(to_user_id)
    if not channel_name:
        raise ValidationError("User is not online.")

    sender = await UserService.get_user_name(from_user_id)
    created_at_str = created_at.isoformat()
    await channel_layer.send(
        channel_name,
        {
            "type": "friend.request",
            "sender": sender,
            "created_at": created_at_str
        }
    )


# 친구 요청 응답
def respond_to_friend_request(request_id, action, user_token):
    try:
        friend_request = FriendRequest.objects.get(id=request_id, status="pending")
    except FriendRequest.DoesNotExist:
        raise NotFound("Friend request not found.")
    
    if action == "accept":
        friend_request.status = "accepted"
        friend_request.save()

        Friendship.objects.create(
            user1=friend_request.from_user,
            user2=friend_request.to_user
        )

        # 채팅방 생성 호출
        asyncio.run(get_chatroom(friend_request.from_user.id, friend_request.to_user.id, user_token))

    elif action == "reject":
        friend_request.status = "rejected"
        friend_request.save()
    else:
        raise ValidationError("Invalid action.")

    return friend_request


# 친구 리스트 조회
def get_friends_list(user):
    friendships = Friendship.objects.filter(Q(user1=user) | Q(user2=user)).select_related('user1', 'user2')
    return [
        {
            "id": friendship.user1.id if friendship.user2 == user else friendship.user2.id,
            "nickname": friendship.user1.nickname if friendship.user2 == user else friendship.user2.nickname,
        }
        for friendship in friendships
    ]