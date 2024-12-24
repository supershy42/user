from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ErrorDetail

def response_ok(message="ok", status=status.HTTP_200_OK):
    if not isinstance(message, dict):
        message = {"message": message}
    return Response(message, status=status)

def response_error(errors):
    if not errors:
        errors = "unknown error."
    return Response(
        {"message": errors},
        status=extract_status(errors)
    )

def extract_status(errors):
    if isinstance(errors, dict):
        for key, value in errors.items():
            if key == "status" and isinstance(value, str) and value.isdigit():
                return int(value)
            elif isinstance(value, dict):
                nested_status = extract_status(value)
                if nested_status:
                    return nested_status
    return status.HTTP_400_BAD_REQUEST