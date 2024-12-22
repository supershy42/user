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

    # 기타 추가된 코드들은 자바 코드와 동일하게 추가 가능

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