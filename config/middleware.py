import jwt
import json
from django.utils.deprecation import MiddlewareMixin
from channels.middleware import BaseMiddleware
from django.http import JsonResponse
from urllib.parse import parse_qs

EXCLUDED_PATHS = [
            '/api/user/register/email-check/',
            '/api/user/register/nickname-check/',
            '/api/user/register/complete/',
            '/api/user/login/',
            '/api/user/2fa/',
            '/media/avatars/',
            '/api/schema/',
]

# HTTP Middleware
class CustomHttpMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if any(request.path.startswith(path) for path in EXCLUDED_PATHS):  # 제외된 경로 처리
            return

        token_line = request.headers.get("Authorization")
        if not token_line:
            return JsonResponse({"error": "Authentication token missing."}, status=401)

        try:
            # JWT 디코딩 및 user_id 추출
            token = token_line.split(" ")[1]
            request.token = token
            payload = jwt.decode(token, options={"verify_signature": False})
            request.user_id = payload.get("user_id")
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=401)


# Websocket Middleware
class CustomWsMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        token = get_jwt(scope)
        if not token:
            return await self.reject_request(send, "Authentication token missing.")

        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            user_id = payload.get('user_id')
            scope['user_id'] = user_id
        except Exception as e:
            return await self.reject_request(send, str(e))

        scope['token'] = token
        return await super().__call__(scope, receive, send)

    # 요청 거부 처리
    async def reject_request(self, send, message, status=401):
        headers = [(b"content-type", b"application/json")]
        body = json.dumps({"error": message}).encode('utf-8')

        await send({
            "type": "http.response.start",
            "status": status,
            "headers": headers,
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })


# JWT 토큰 추출
def get_jwt(scope):
    query_string = scope.get('query_string', b'').decode()
    query_params = parse_qs(query_string)
    token = query_params.get('token', [None])[0]
    return token