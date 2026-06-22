"""
Management command: fetch_disruptions
Polls the Darwin API disruption feed and stores active disruptions.
"""
import logging
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from rail.models import Disruption
from rail.services import get_darwin_client, DarwinAPIError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fetch current rail disruptions from the Darwin API and store them in the database.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear', action='store_true',
            help='Mark all existing disruptions as inactive before fetching.'
        )

    def handle(self, *args, **options):
        try:
            client = get_darwin_client()
            disruptions = client.get_disruptions()
        except DarwinAPIError as e:
            raise CommandError(f'Darwin API error: {e}')
        except Exception as e:
            raise CommandError(f'Unexpected error: {e}')

        if options['clear']:
            Disruption.objects.filter(is_active=True).update(is_active=False)
            self.stdout.write(self.style.WARNING('Marked all existing disruptions as inactive.'))

        if not disruptions:
            self.stdout.write(self.style.SUCCESS('No disruptions returned from API.'))
            return

        created = 0
        updated = 0

        for data in disruptions:
            start_time = self._parse_datetime(data.get('start_time'))
            end_time = self._parse_datetime(data.get('end_time'))

            obj, was_created = Disruption.objects.update_or_create(
                incident_id=data.get('incident_id', ''),
                defaults={
                    'type': data.get('type', ''),
                    'summary': data.get('summary', ''),
                    'description': data.get('description', ''),
                    'start_time': start_time or timezone.now(),
                    'end_time': end_time,
                    'affected_routes': data.get('affected_routes', ''),
                    'severity': data.get('severity', 'medium'),
                    'is_active': True,
                }
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f'Fetched {len(disruptions)} disruptions: {created} created, {updated} updated.'
        ))

    @staticmethod
    def _parse_datetime(dt_str):
        """Parse an ISO datetime string; return None on failure."""
        if not dt_str:
            return None
        try:
            # Handle ISO 8601 with or without timezone
            if 'T' in dt_str:
                return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            return datetime.fromisoformat(dt_str)
        except (ValueError, TypeError):
            return None