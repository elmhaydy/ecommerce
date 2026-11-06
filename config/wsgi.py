"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import sys
import logging
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

# Auto-apply migrations and seed data on startup (ensures DB is always ready on Render)
try:
    print("==> [WSGI startup] Running database migrations...", flush=True)
    from django.core.management import call_command
    call_command("migrate", interactive=False)
    print("==> [WSGI startup] Migrations completed successfully!", flush=True)

    print("==> [WSGI startup] Checking/seeding initial database data...", flush=True)
    call_command("seed_db", auto=True)
    print("==> [WSGI startup] Database ready!", flush=True)
except Exception as exc:
    import traceback
    print("==> [WSGI startup WARNING] Database migration or seed notice:", flush=True)
    traceback.print_exc()
    sys.stdout.flush()
    sys.stderr.flush()
