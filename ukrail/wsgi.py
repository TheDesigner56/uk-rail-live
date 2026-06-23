"""WSGI config for UK Rail Live."""
import os
import shutil
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ukrail.settings')

# On Vercel: set up SQLite in /tmp (writable) and load seed data on cold start
if os.environ.get('VERCEL'):
    import django
    django.setup()
    from django.core.management import call_command
    
    # Run migrations (creates tables in /tmp/db.sqlite3)
    try:
        call_command('migrate', '--run-syncdb', verbosity=0, interactive=False)
    except Exception as e:
        import logging
        logging.getLogger('rail').error(f'Auto-migrate failed: {e}')
    
    # Load seed data if DB is empty
    try:
        from rail.models import Station
        if Station.objects.count() == 0:
            call_command('loaddata', 'rail/fixtures/stations.json', verbosity=0)
            import logging
            logging.getLogger('rail').info(f'Loaded {Station.objects.count()} stations from fixture')
    except Exception as e:
        import logging
        logging.getLogger('rail').error(f'Load fixture failed: {e}')

from django.core.wsgi import get_wsgi_application  # noqa: E402
application = get_wsgi_application()