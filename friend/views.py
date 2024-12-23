from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound
from drf_spectacular.utils import extend_schema
from asgiref.sync import async_to_sync
from rest_framework.views import APIView
from .services import (
    send_friend_request,
    respond_to_friend_request,
    get_friends_list,
    delete_friend
)


class SendFriendRequestView(APIView):
    def post(self, request):
        to_user_id = request.data.get('to_user_id')
        try:
            async_to_sync(send_friend_request)(request.user_id, to_user_id)
            return Response({"message": "Friend request sent successfully"}, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except NotFound as e:
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)


class RespondToFriendRequestView(APIView):
    def post(self, request):
        friend_request_id = request.data.get('friend_request_id')
        action = request.data.get('action')
        try:
            respond_to_friend_request(friend_request_id, action, request.token)
            return Response(
                {"message": f"Friend request {action}ed"},
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except NotFound as e:
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)


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
        friends = get_friends_list(request.user)
        if friends is None:
            return Response(
                {"message": "Friends list is not initialized or unavailable."},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(friends, status=status.HTTP_200_OK)


class DeleteFriendView(APIView):
    def post(self, request):
        friend_id = request.data.get('friend_id')
        try:
            delete_friend(request.user_id, friend_id, request.token)
            return Response({"message": "Friend deleted successfully"}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except NotFound as e:
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)