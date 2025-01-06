import os

from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application

# Set the settings module for the 'asgi' application before importing any Django modules
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")


# Define the ASGI application
application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
    }
)
