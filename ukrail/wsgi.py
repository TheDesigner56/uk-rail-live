"""WSGI config for UK Rail Live."""
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ukrail.settings')

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()