from django.contrib.auth import get_user_model
from django.db.models import Q
from config.services import get_chatroom, delete_chatroom
from channels.layers import get_channel_layer
from user_management.redis_utils import get_channel_name
from asgiref.sync import async_to_sync
from django.db import transaction
from .models import FriendRequest, Friendship
from user_management.services import UserService
from config.custom_validation_error import CustomValidationError
from config.error_type import ErrorType

User = get_user_model()

class FriendService:
    @staticmethod
    async def send_friend_request(from_user_id, nickname):
        try:
            from_user = await User.objects.aget(id=from_user_id)
            to_user = await User.objects.aget(nickname=nickname)
        except User.DoesNotExist:
            raise CustomValidationError(ErrorType.USER_NOT_FOUND)

        if from_user == to_user:
            raise CustomValidationError(ErrorType.SELF_FRIEND_REQUEST)

        if await FriendRequest.objects.filter(Q(from_user=from_user, to_user=to_user) | Q(from_user=to_user, to_user=from_user)).aexists():
            raise CustomValidationError(ErrorType.FRIEND_REQUEST_ALREADY_EXISTS)

        if await Friendship.objects.filter(Q(user1=from_user, user2=to_user) | Q(user1=to_user, user2=from_user)).aexists():
            raise CustomValidationError(ErrorType.ALREADY_FRIENDS)

        friend_request = await FriendRequest.objects.acreate(from_user=from_user, to_user=to_user, status="pending")
        await FriendService.send_friend_request_notification(from_user_id, to_user.id, friend_request.id, friend_request.created_at)


    @staticmethod
    async def send_friend_request_notification(from_user_id, to_user_id, friend_request_id, created_at):
        channel_layer = get_channel_layer()
        channel_name = await get_channel_name(to_user_id)
        if not channel_name:
            return

        sender = await UserService.get_user_name(from_user_id)
        created_at_str = created_at.isoformat()
        await channel_layer.send(
            channel_name,
            {
                "type": "friend.request",
                "friend_request_id": friend_request_id,
                "sender": sender,
                "created_at": created_at_str
            }
        )


    @staticmethod
    def respond_to_friend_request(request_id, action, token):
        try:
            friend_request = FriendRequest.objects.get(id=request_id, status="pending")
        except FriendRequest.DoesNotExist:
            raise CustomValidationError(ErrorType.FRIEND_REQUEST_NOT_FOUND)

        if action not in ["accept", "reject"]:
            raise CustomValidationError(ErrorType.VALIDATION_ERROR)

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
                    raise CustomValidationError(ErrorType.CHATROOM_CREATION_FAILED)

                # ChatRoom ID 저장
                friendship.chatroom_id = chatroom_data['id']
                friendship.save()

            elif action == "reject":
                friend_request.status = "rejected"
                friend_request.save()


    @staticmethod
    def get_received_friend_requests(user_id):
        return FriendRequest.objects.filter(
            to_user_id = user_id,
            status = "pending"
        ).values("from_user__nickname", "created_at")


    @staticmethod
    def get_friends_list(user):
        friendships = Friendship.objects.filter(Q(user1=user) | Q(user2=user)).select_related('user1', 'user2')
        return [
            {
                "id": friendship.user1.id if friendship.user2 == user else friendship.user2.id,
                "nickname": friendship.user1.nickname if friendship.user2 == user else friendship.user2.nickname,
            }
            for friendship in friendships
        ]


    @staticmethod
    def delete_friend(user_id, friend_id, token):
        try:
            user = User.objects.get(id=user_id)
            friend = User.objects.get(id=friend_id)
        except User.DoesNotExist:
            raise CustomValidationError(ErrorType.USER_NOT_FOUND)

        try:
            friendship = Friendship.objects.get(Q(user1=user, user2=friend) | Q(user1=friend, user2=user))
        except Friendship.DoesNotExist:
            raise CustomValidationError(ErrorType.FRIENDSHIP_NOT_FOUND)

        FriendRequest.objects.filter(Q(from_user=user, to_user=friend) | Q(from_user=friend, to_user=user)).delete()

        # ChatRoom 삭제 API 호출
        is_chatroom_deleted = async_to_sync(delete_chatroom)(friendship.chatroom_id, token)
        if not is_chatroom_deleted:
            raise CustomValidationError(ErrorType.CHATROOM_DELETION_FAILED)

        friendship.delete()