import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import awesome_app.routing 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'awesome_project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
        awesome_app.routing.websocket_urlpatterns,
    ),
})
