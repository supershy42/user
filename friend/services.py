from .models import FriendRequest, Friendship
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError, NotFound
from django.db.models import Q
from config.services import get_chatroom, delete_chatroom
from channels.layers import get_channel_layer
from user_management.redis_utils import get_channel_name
from user_management.services import UserService
from asgiref.sync import async_to_sync
from django.db import transaction


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
def respond_to_friend_request(request_id, action, token):
    try:
        friend_request = FriendRequest.objects.get(id=request_id, status="pending")
    except FriendRequest.DoesNotExist:
        raise NotFound("Friend request not found.")
    
    if action not in ["accept", "reject"]:
        raise ValidationError("Invalid action.")

    with transaction.atomic():
        if action == "accept":
            friend_request.status = "accepted"
            friend_request.save()

            friendship = Friendship.objects.create(
                user1=friend_request.from_user,
                user2=friend_request.to_user
            )

            # ChatRoom 생성 API 호출
            chatroom_data = async_to_sync(get_chatroom)(
                friend_request.from_user.id,
                friend_request.to_user.id,
                token
            )
            if chatroom_data is None:
                raise ValidationError("Chatroom creation failed.")
            
            # ChatRoom ID 저장
            friendship.chatroom_id = chatroom_data['id']
            friendship.save()

        elif action == "reject":
            friend_request.status = "rejected"
            friend_request.save()


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


# 친구 삭제
def delete_friend(user_id, friend_id, token):
    try:
        user = User.objects.get(id=user_id)
        friend = User.objects.get(id=friend_id)
    except User.DoesNotExist:
        raise NotFound("User not found.")

    try:
        friendship = Friendship.objects.get(Q(user1=user, user2=friend) | Q(user1=friend, user2=user))
    except Friendship.DoesNotExist:
        raise ValidationError("You are not friends.")
    
    FriendRequest.objects.filter(Q(from_user=user, to_user=friend) | Q(from_user=friend, to_user=user)).delete()

    # ChatRoom 삭제 API 호출
    is_chatroom_deleted = async_to_sync(delete_chatroom)(friendship.chatroom_id, token)
    if not is_chatroom_deleted:
        raise ValidationError("Chatroom deletion failed.")

    friendship.delete()