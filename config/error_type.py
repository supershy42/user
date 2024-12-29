from enum import Enum
from rest_framework import status


class ErrorType(Enum):
    # user
    NICKNAME_ALREADY_EXISTS = (status.HTTP_409_CONFLICT, "This nickname is already in use.")
    EMAIL_ALREADY_EXISTS = (status.HTTP_409_CONFLICT, "This email is already in use.")
    INVALID_VERIFICATION_CODE = (status.HTTP_400_BAD_REQUEST, "Invalid verification code.")
    VERIFICATION_CODE_EXPIRED = (status.HTTP_400_BAD_REQUEST, "The verification code has expired.")
    VALIDATION_ERROR = (status.HTTP_400_BAD_REQUEST, "One or more fields failed validation. Please check the input values.")
    INVALID_CREDENTIALS = (status.HTTP_401_UNAUTHORIZED, "Invalid credentials.")
    USER_NOT_FOUND = (status.HTTP_404_NOT_FOUND, "User not found.")
    USER_ID_NOT_FOUND = (status.HTTP_400_BAD_REQUEST, "The user_id parameter is missing in the request URL.")
    INVALID_EMAIL_REQUEST = (status.HTTP_400_BAD_REQUEST, "The email sending request is invalid.")

    # common
    FIELD_REQUIRED = (status.HTTP_400_BAD_REQUEST, "some fields are missing.")

    # friend
    FRIEND_REQUEST_ALREADY_EXISTS = (status.HTTP_409_CONFLICT, "Friend request already exists or received.")
    SELF_FRIEND_REQUEST = (status.HTTP_400_BAD_REQUEST, "You cannot send a friend request to yourself.")
    ALREADY_FRIENDS = (status.HTTP_409_CONFLICT, "You are already friends.")
    FRIEND_REQUEST_NOT_FOUND = (status.HTTP_404_NOT_FOUND, "Friend request not found.")
    CHATROOM_CREATION_FAILED = (status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create a chatroom.")
    FRIENDSHIP_NOT_FOUND = (status.HTTP_404_NOT_FOUND, "Friendship not found.")
    CHATROOM_DELETION_FAILED = (status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to delete the chatroom.")
    FRIENDS_LIST_UNAVAILABLE = (status.HTTP_404_NOT_FOUND, "Friends list is not initialized or unavailable.")
    FRIEND_REQUEST_BLOCKED = (status.HTTP_403_FORBIDDEN, "Friend request blocked due to existing block relationship.")
    BLOCK_ALREADY_EXISTS = (status.HTTP_409_CONFLICT, "Block relationship already exists.")
    BLOCK_NOT_FOUND = (status.HTTP_404_NOT_FOUND, "Block relationship not found.")
    
    def __init__(self, status, message):
        self.status = status
        self.message = message

    def to_dict(self):
        return {
            "status": self.status,
            "message": self.message
        }

    @staticmethod
    def find_by_message(message):
        for error in ErrorType:
            if error.message == message:
                return error
        return None