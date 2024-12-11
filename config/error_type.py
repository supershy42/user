from enum import Enum
from rest_framework import status


class ErrorType(Enum):
    # common
    BUSINESS_EXCEPTION = (500, "BUSINESS ERROR")
    NULL_POINT = (500, "NULL POINT EXCEPTION")

    # user
    CONFLICT_NICKNAME = (status.HTTP_409_CONFLICT, "This nickname is already in use.")
    USER_NOT_FOUND = (404, "USER NOT FOUND")
    USER_IMAGE_NOT_FOUND = (404, "USER IMAGE NOT FOUND")
    USER_IMAGE_TOO_LARGE = (413, "USER IMAGE IS TOO LARGE")
    USER_IMAGE_WRONG_TYPE = (415, "USER IMAGE TYPE IS WRONG")
    KAKAO_OAUTH2_NOT_FOUND = (404, "KAKAO OAUTH2 NOT FOUND")
    KAKAO_OAUTH2_DUPLICATE = (409, "KAKAO OAUTH2 ALREADY EXIST")
    USER_TEXT_COLOR_WRONG_TYPE = (401, "USER TEXT COLOR CODE IS WRONG")
    USER_ALREADY_ATTENDANCE = (409, "USER ALREADY ATTENDANCE")

    # announcement
    ANNOUNCE_NOT_FOUND = (404, "ANNOUNCEMENT NOT FOUND")
    ANNOUNCE_DUPLICATE = (409, "ANNOUNCEMENT DUPLICATION")

    # coinPolicy
    COIN_POLICY_NOT_FOUND = (404, "COINPOLICY NOT FOUND")

    # coinHistory
    COIN_HISTORY_NOT_FOUND = (404, "COIN HISTORY NOT FOUND")

    # season
    SEASON_NOT_FOUND = (404, "SEASON NOT FOUND")
    SEASON_FORBIDDEN = (400, "SEASON FORBIDDEN ERROR")
    SEASON_TIME_BEFORE = (400, "SEASON TIME BEFORE")

    # slotmanagement
    SLOTMANAGEMENT_NOT_FOUND = (404, "SLOTMANAGEMENT NOT FOUND")
    SLOTMANAGEMENT_FORBIDDEN = (400, "SLOTMANAGEMENT FORBIDDEN")

    # rank
    RANK_NOT_FOUND = (404, "RANK NOT FOUND")
    REDIS_RANK_NOT_FOUND = (404, "REDIS RANK NOT FOUND")
    RANK_UPDATE_FAIL = (400, "RANK UPDATE FAIL")

    # 기타 추가된 코드들은 자바 코드와 동일하게 추가 가능

    def __init__(self, status, message):
        self.status = status
        self.message = message

    def to_dict(self):
        """
        Convert the error code to a dictionary format for easy use in APIs.
        """
        return {
            "status": self.status,
            "message": self.message
        }

    @staticmethod
    def find_by_message(message):
        """
        Find an error by its message.
        """
        for error in ErrorType:
            if error.message == message:
                return error
        return None