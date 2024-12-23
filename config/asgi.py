import os
from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from user_management.routing import websocket_urlpatterns
from .middleware import CustomWsMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": CustomWsMiddleware(
        URLRouter(websocket_urlpatterns)
    )
})