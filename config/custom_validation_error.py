from rest_framework.exceptions import ValidationError

class CustomValidationError(ValidationError):
    def __init__(self, error_type, code=None):
        detail = error_type.to_dict()
        super().__init__(detail, code)