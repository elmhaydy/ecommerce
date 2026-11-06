"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import logging
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

# Auto-apply migrations and seed data on startup (ensures DB is always ready on Render)
try:
    from django.core.management import call_command
    call_command("migrate", interactive=False)
    call_command("seed_db", auto=True)
except Exception as exc:
    logger = logging.getLogger("config.wsgi")
    logger.warning("Startup database migration/seed check encountered an issue: %s", exc)
