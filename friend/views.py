from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound
from drf_spectacular.utils import extend_schema
from asgiref.sync import async_to_sync
from rest_framework.views import APIView
from .services import FriendService
from config.response_builder import response_ok, response_errors
from config.custom_validation_error import CustomValidationError
from config.error_type import ErrorType

class SendFriendRequestView(APIView):
    def post(self, request):
        nickname = request.data.get('nickname')
        if not nickname:
            return response_errors(errors=CustomValidationError(ErrorType.FIELD_REQUIRED))
        try:
            async_to_sync(FriendService.send_friend_request)(request.user_id, nickname)
            return response_ok(status=status.HTTP_201_CREATED)
        except CustomValidationError as e:
            return response_errors(errors=e)


class RespondToFriendRequestView(APIView):
    def post(self, request):
        friend_request_id = request.data.get('friend_request_id')
        action = request.data.get('action')
        try:
            FriendService.respond_to_friend_request(friend_request_id, action, request.token)
            return response_ok({"message": f"Friend request {action}ed"})
        except CustomValidationError as e:
            return response_errors(errors=e)


class ReceivedFriendRequestListView(APIView):
    def get(self, request):
        try:
            user_id = request.user_id
            friend_requests = FriendService.get_received_friend_requests(user_id)

            requests = [
                {
                    "from_user": friend_request["from_user__nickname"],
                    "created_at": friend_request["created_at"].isoformat(),
				}
                for friend_request in friend_requests
			]
            return response_ok(data=requests)
        except CustomValidationError as e:
            return response_errors(errors=e)


class FriendListView(APIView):
    @extend_schema(
        summary="Get the friend list of the authenticated user",
        responses={
            200: "Successfully retrieved the friend list.",
            401: "Authentication credentials were not provided or invalid.",
            404: "Friends list is not initialized or unavailable.",
        },
    )
    def get(self, request):
        friends = FriendService.get_friends_list(request.user)
        if friends is None:
            return response_errors(errors=CustomValidationError(ErrorType.FRIENDS_LIST_UNAVAILABLE))
        return response_ok(data=friends)


class DeleteFriendView(APIView):
    def post(self, request):
        friend_id = request.data.get('friend_id')
        try:
            FriendService.delete_friend(request.user_id, friend_id, request.token)
            return response_ok()
        except CustomValidationError as e:
            return response_errors(errors=e)