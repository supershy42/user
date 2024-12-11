from rest_framework.response import Response
from rest_framework import status

def response_ok(message="ok", status=status.HTTP_200_OK):
    if not isinstance(message, dict):
        message = {"message": message}
    return Response(message, status=status)

def response_error(errors):
    message = extract_message(errors)
    if not message:
        message = {"message": "unknown error."}
    return Response(
        message,
        status=extract_status(errors)
    )
    
def extract_status(errors):
    for key, value in errors.items():
        if isinstance(value, dict) and "status" in value:
            return value["status"]
    return status.HTTP_400_BAD_REQUEST

def extract_message(errors):
    message = None
    if isinstance(errors, dict):
        error = next(iter(errors.values()))
        if isinstance(error, dict) and "message" in error:
            message = {"message": error["message"]}
    return message