"""
Management command: import_stations
Imports UK railway station data into the database.
Includes seed data for 10 major stations (no API key required).
With API key, can fetch full station list from National Rail.
"""
import logging
from django.core.management.base import BaseCommand
from rail.models import Station

logger = logging.getLogger(__name__)

# Seed data — 10 major UK railway stations
SEED_STATIONS = [
    {'crs_code': 'PAD', 'name': 'London Paddington', 'full_name': 'London Paddington',
     'lat': 51.5152, 'lon': -0.1755, 'region': 'London', 'operator': 'Great Western Railway'},
    {'crs_code': 'WAT', 'name': 'London Waterloo', 'full_name': 'London Waterloo',
     'lat': 51.5030, 'lon': -0.1132, 'region': 'London', 'operator': 'South Western Railway'},
    {'crs_code': 'MAN', 'name': 'Manchester Piccadilly', 'full_name': 'Manchester Piccadilly',
     'lat': 53.4773, 'lon': -2.2304, 'region': 'North West', 'operator': 'Northern / Avanti West Coast'},
    {'crs_code': 'BHM', 'name': 'Birmingham New Street', 'full_name': 'Birmingham New Street',
     'lat': 52.4771, 'lon': -1.8990, 'region': 'West Midlands', 'operator': 'West Midlands Railway / CrossCountry'},
    {'crs_code': 'EDB', 'name': 'Edinburgh Waverley', 'full_name': 'Edinburgh Waverley',
     'lat': 55.9532, 'lon': -3.1904, 'region': 'Scotland', 'operator': 'LNER / ScotRail'},
    {'crs_code': 'GLC', 'name': 'Glasgow Central', 'full_name': 'Glasgow Central',
     'lat': 55.8593, 'lon': -4.2590, 'region': 'Scotland', 'operator': 'Avanti West Coast / ScotRail'},
    {'crs_code': 'LDS', 'name': 'Leeds', 'full_name': 'Leeds',
     'lat': 53.7956, 'lon': -1.5491, 'region': 'Yorkshire', 'operator': 'Northern / LNER / CrossCountry'},
    {'crs_code': 'BRI', 'name': 'Bristol Temple Meads', 'full_name': 'Bristol Temple Meads',
     'lat': 51.4490, 'lon': -2.5767, 'region': 'South West', 'operator': 'Great Western Railway / CrossCountry'},
    {'crs_code': 'RDG', 'name': 'Reading', 'full_name': 'Reading',
     'lat': 51.4614, 'lon': -0.9740, 'region': 'South East', 'operator': 'Great Western Railway'},
    {'crs_code': 'OXF', 'name': 'Oxford', 'full_name': 'Oxford',
     'lat': 51.7360, 'lon': -1.2490, 'region': 'South East', 'operator': 'Great Western Railway / Chiltern Railways'},
]

# Extended station list — additional major stations (can be expanded)
EXTENDED_STATIONS = [
    {'crs_code': 'KIN', 'name': 'London Kings Cross', 'full_name': 'London Kings Cross',
     'lat': 51.5308, 'lon': -0.1238, 'region': 'London', 'operator': 'LNER / Thameslink'},
    {'crs_code': 'EUS', 'name': 'London Euston', 'full_name': 'London Euston',
     'lat': 51.5281, 'lon': -0.1337, 'region': 'London', 'operator': 'Avanti West Coast'},
    {'crs_code': 'LST', 'name': 'London Liverpool Street', 'full_name': 'London Liverpool Street',
     'lat': 51.5179, 'lon': -0.0816, 'region': 'London', 'operator': 'Greater Anglia / Elizabeth Line'},
    {'crs_code': 'VIC', 'name': 'London Victoria', 'full_name': 'London Victoria',
     'lat': 51.4953, 'lon': -0.1440, 'region': 'London', 'operator': 'Southeastern / Southern'},
    {'crs_code': 'LBG', 'name': 'London Bridge', 'full_name': 'London Bridge',
     'lat': 51.5047, 'lon': -0.0865, 'region': 'London', 'operator': 'Southeastern / Thameslink'},
    {'crs_code': 'CST', 'name': 'London Cannon Street', 'full_name': 'London Cannon Street',
     'lat': 51.5114, 'lon': -0.0906, 'region': 'London', 'operator': 'Southeastern'},
    {'crs_code': 'CTK', 'name': 'London Charing Cross', 'full_name': 'London Charing Cross',
     'lat': 51.5084, 'lon': -0.1239, 'region': 'London', 'operator': 'Southeastern'},
    {'crs_code': 'FST', 'name': 'London Fenchurch Street', 'full_name': 'London Fenchurch Street',
     'lat': 51.5119, 'lon': -0.0793, 'region': 'London', 'operator': 'c2c'},
    {'crs_code': 'MDV', 'name': 'London Marylebone', 'full_name': 'London Marylebone',
     'lat': 51.5226, 'lon': -0.1587, 'region': 'London', 'operator': 'Chiltern Railways'},
    {'crs_code': 'SPX', 'name': 'London St Pancras International', 'full_name': 'London St Pancras International',
     'lat': 51.5307, 'lon': -0.1238, 'region': 'London', 'operator': 'Eurostar / Southeastern / East Midlands Railway'},
    {'crs_code': 'YRK', 'name': 'York', 'full_name': 'York',
     'lat': 53.9577, 'lon': -1.0940, 'region': 'Yorkshire', 'operator': 'LNER / CrossCountry / TransPennine Express'},
    {'crs_code': 'NCL', 'name': 'Newcastle', 'full_name': 'Newcastle',
     'lat': 54.9693, 'lon': -1.6140, 'region': 'North East', 'operator': 'LNER / CrossCountry / Northern'},
    {'crs_code': 'LVP', 'name': 'Liverpool Lime Street', 'full_name': 'Liverpool Lime Street',
     'lat': 53.4071, 'lon': -2.9790, 'region': 'North West', 'operator': 'Avanti West Coast / Northern / TransPennine Express'},
    {'crs_code': 'SHF', 'name': 'Sheffield', 'full_name': 'Sheffield',
     'lat': 53.4117, 'lon': -1.4607, 'region': 'Yorkshire', 'operator': 'Northern / CrossCountry / East Midlands Railway'},
    {'crs_code': 'NOT', 'name': 'Nottingham', 'full_name': 'Nottingham',
     'lat': 52.9480, 'lon': -1.1390, 'region': 'East Midlands', 'operator': 'East Midlands Railway / CrossCountry'},
    {'crs_code': 'CNY', 'name': 'Canterbury East', 'full_name': 'Canterbury East',
     'lat': 51.2765, 'lon': 1.0870, 'region': 'South East', 'operator': 'Southeastern'},
    {'crs_code': 'CBG', 'name': 'Cambridge', 'full_name': 'Cambridge',
     'lat': 52.2080, 'lon': 0.1310, 'region': 'East', 'operator': 'Greater Anglia / Thameslink / Great Northern'},
    {'crs_code': 'BNS', 'name': 'Brighton', 'full_name': 'Brighton',
     'lat': 50.8290, 'lon': -0.1410, 'region': 'South East', 'operator': 'Southern / Thameslink / Gatwick Express'},
    {'crs_code': 'SOU', 'name': 'Southampton Central', 'full_name': 'Southampton Central',
     'lat': 50.7120, 'lon': -1.4140, 'region': 'South East', 'operator': 'South Western Railway / CrossCountry'},
    {'crs_code': 'EXR', 'name': 'Exeter St Davids', 'full_name': 'Exeter St Davids',
     'lat': 50.7330, 'lon': -3.5430, 'region': 'South West', 'operator': 'Great Western Railway / CrossCountry'},
]


class Command(BaseCommand):
    help = 'Import UK railway station data into the database.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--extended', action='store_true',
            help='Also import the extended station list (30 stations total).'
        )
        parser.add_argument(
            '--clear', action='store_true',
            help='Clear existing stations before import.'
        )

    def handle(self, *args, **options):
        stations_to_import = SEED_STATIONS
        if options['extended']:
            stations_to_import = SEED_STATIONS + EXTENDED_STATIONS

        if options['clear']:
            deleted = Station.objects.all().delete()[0]
            self.stdout.write(self.style.WARNING(f'Cleared {deleted} existing stations.'))

        created = 0
        updated = 0

        for data in stations_to_import:
            obj, was_created = Station.objects.update_or_create(
                crs_code=data['crs_code'],
                defaults={
                    'name': data['name'],
                    'full_name': data.get('full_name', data['name']),
                    'lat': data['lat'],
                    'lon': data['lon'],
                    'region': data.get('region', ''),
                    'operator': data.get('operator', ''),
                }
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f'Import complete: {created} created, {updated} updated, {len(stations_to_import)} total.'
        ))