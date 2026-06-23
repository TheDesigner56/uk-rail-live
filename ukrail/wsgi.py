"""WSGI config for UK Rail Live."""
import os
import shutil
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ukrail.settings')

# On Vercel: copy bundled SQLite to /tmp (writable) and load seed data on cold start
if os.environ.get('VERCEL'):
    bundled_db = Path(__file__).resolve().parent.parent / 'db.sqlite3'
    tmp_db = Path('/tmp/db.sqlite3')
    if bundled_db.exists() and not tmp_db.exists():
        shutil.copy2(str(bundled_db), str(tmp_db))

    import django
    django.setup()
    from django.core.management import call_command
    try:
        call_command('migrate', '--run-syncdb', verbosity=0, interactive=False)
    except Exception as e:
        import logging
        logging.getLogger('rail').error(f'Auto-migrate failed: {e}')

    # Load seed data if DB is empty
    from rail.models import Station
    if Station.objects.count() == 0:
        try:
            call_command('loaddata', 'rail/fixtures/stations.json', verbosity=0)
        except Exception as e:
            import logging
            logging.getLogger('rail').error(f'Load fixture failed: {e}')

from django.core.wsgi import get_wsgi_application  # noqa: E402
application = get_wsgi_application()