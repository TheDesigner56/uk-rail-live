#!/bin/bash
# Vercel build script for UK Rail Live
set -e

echo "Running collectstatic..."
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ukrail.settings')
import django
django.setup()
from django.core.management import call_command
call_command('collectstatic', '--noinput', verbosity=2)
"

echo "Build complete."