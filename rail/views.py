"""Views for UK Rail Live."""
import logging
from datetime import timedelta

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET
from django.db.models import Q
from django.utils import timezone

from .models import Station, Service, Disruption
from .services import get_darwin_client, DarwinAPIError

logger = logging.getLogger(__name__)


# ── Homepage ───────────────────────────────────────────────────────────────

def homepage(request):
    """Homepage with search, map, and live disruptions."""
    stations = Station.objects.all().order_by('name')
    major_stations = stations.filter(
        crs_code__in=['PAD', 'WAT', 'MAN', 'BHM', 'EDB', 'GLC', 'LDS', 'BRI', 'RDG', 'OXF']
    )
    disruptions = Disruption.objects.filter(is_active=True)[:10]

    # Build GeoJSON for mini map
    features = []
    for s in stations.values('crs_code', 'name', 'lat', 'lon', 'region'):
        features.append({
            'type': 'Feature',
            'geometry': {'type': 'Point', 'coordinates': [s['lon'], s['lat']]},
            'properties': {'crs': s['crs_code'], 'name': s['name'], 'region': s['region']},
        })
    import json
    geojson = json.dumps({'type': 'FeatureCollection', 'features': features})

    context = {
        'stations': major_stations,
        'all_stations': stations,
        'disruptions': disruptions,
        'station_count': stations.count(),
        'geojson': geojson,
        'meta_description': 'UK Rail Live — real-time train departures, arrivals, and disruption information for every UK railway station.',
        'meta_keywords': 'UK trains, train times, live departures, rail disruptions, National Rail, train tracker',
        'page_title': 'UK Rail Live — Real-Time Train Departures & Disruptions',
    }
    return render(request, 'rail/homepage.html', context)


# ── Station views ─────────────────────────────────────────────────────────

def station_list(request):
    """All stations list."""
    stations = Station.objects.all().order_by('name')
    context = {
        'stations': stations,
        'page_title': 'All UK Railway Stations — UK Rail Live',
        'meta_description': 'Complete list of all UK railway stations with live departure boards. Search by name or CRS code.',
    }
    return render(request, 'rail/station_list.html', context)


def station_detail(request, crs):
    """Station page with live departures and arrivals."""
    station = get_object_or_404(Station, crs_code__iexact=crs.upper())

    departures = []
    arrivals = []
    api_error = None

    try:
        client = get_darwin_client()
        departures = client.get_departures(station.crs_code)
        arrivals = client.get_arrivals(station.crs_code)
    except DarwinAPIError as e:
        api_error = str(e)
        logger.warning('Darwin API error for %s: %s', station.crs_code, e)
    except Exception as e:
        api_error = 'Unable to fetch live data at this time.'
        logger.error('Unexpected error fetching data for %s: %s', station.crs_code, e)

    context = {
        'station': station,
        'departures': departures,
        'arrivals': arrivals,
        'api_error': api_error,
        'page_title': f'{station.name} Live Departures & Arrivals — UK Rail Live',
        'meta_description': f'Live train departures and arrivals at {station.name} ({station.crs_code}). Real-time platform information, delays, and cancellations.',
        'meta_keywords': f'{station.name}, {station.crs_code}, train times, departures, arrivals, live board',
        'structured_data': {
            '@context': 'https://schema.org',
            '@type': 'TrainStation',
            'name': station.name,
            'identifier': station.crs_code,
            'geo': {
                '@type': 'GeoCoordinates',
                'latitude': station.lat,
                'longitude': station.lon,
            },
            'address': {
                '@type': 'PostalAddress',
                'addressRegion': station.region,
            },
        },
    }
    return render(request, 'rail/station_detail.html', context)


@require_GET
def station_departures_partial(request, crs):
    """HTMX partial: departures board only (auto-refresh target)."""
    station = get_object_or_404(Station, crs_code__iexact=crs.upper())
    departures = []
    api_error = None

    try:
        client = get_darwin_client()
        departures = client.get_departures(station.crs_code)
    except DarwinAPIError as e:
        api_error = str(e)
    except Exception:
        api_error = 'Unable to fetch live data at this time.'

    context = {
        'station': station,
        'departures': departures,
        'api_error': api_error,
    }
    return render(request, 'rail/partials/_departures.html', context)


@require_GET
def station_arrivals_partial(request, crs):
    """HTMX partial: arrivals board only (auto-refresh target)."""
    station = get_object_or_404(Station, crs_code__iexact=crs.upper())
    arrivals = []
    api_error = None

    try:
        client = get_darwin_client()
        arrivals = client.get_arrivals(station.crs_code)
    except DarwinAPIError as e:
        api_error = str(e)
    except Exception:
        api_error = 'Unable to fetch live data at this time.'

    context = {
        'station': station,
        'arrivals': arrivals,
        'api_error': api_error,
    }
    return render(request, 'rail/partials/_arrivals.html', context)


# ── Service detail ─────────────────────────────────────────────────────────

def service_detail(request, rid):
    """Individual service detail page."""
    service_detail_data = None
    api_error = None

    try:
        client = get_darwin_client()
        service_detail_data = client.get_service(rid)
    except DarwinAPIError as e:
        api_error = str(e)
    except Exception:
        api_error = 'Unable to fetch service details at this time.'

    context = {
        'rid': rid,
        'service': service_detail_data,
        'api_error': api_error,
        'page_title': f'Service {rid} — UK Rail Live',
        'meta_description': f'Real-time tracking for train service {rid}. Live updates, calling points, and platform information.',
    }
    return render(request, 'rail/service_detail.html', context)


# ── Disruptions ───────────────────────────────────────────────────────────

def disruption_list(request):
    """Network-wide disruption feed."""
    disruptions = Disruption.objects.filter(is_active=True).order_by('-start_time')
    context = {
        'disruptions': disruptions,
        'page_title': 'Live Rail Disruptions — UK Rail Live',
        'meta_description': 'Real-time UK rail network disruptions, incidents, and service updates. See delays, cancellations, and engineering works.',
    }
    return render(request, 'rail/disruption_list.html', context)


def disruption_detail(request, incident_id):
    """Individual disruption detail page."""
    disruption = get_object_or_404(Disruption, incident_id=incident_id)
    context = {
        'disruption': disruption,
        'page_title': f'{disruption.summary} — UK Rail Live',
        'meta_description': disruption.summary,
    }
    return render(request, 'rail/disruption_detail.html', context)


# ── Map ─────────────────────────────────────────────────────────────────

def map_view(request):
    """Full-screen map of all stations."""
    import json
    stations = Station.objects.all().values('crs_code', 'name', 'lat', 'lon', 'region')

    # Build station GeoJSON
    features = []
    for s in stations:
        features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [s['lon'], s['lat']],
            },
            'properties': {
                'crs': s['crs_code'],
                'name': s['name'],
                'region': s['region'],
            },
        })

    geojson = json.dumps({
        'type': 'FeatureCollection',
        'features': features,
    })

    context = {
        'geojson': geojson,
        'page_title': 'UK Railway Station Map — UK Rail Live',
        'meta_description': 'Interactive map of all UK railway stations. Click any station to view live departures and arrivals.',
    }
    return render(request, 'rail/map.html', context)


# ── Search ────────────────────────────────────────────────────────────────

def search(request):
    """Search for stations by name or CRS code."""
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        if len(query) <= 3 and query.isalpha():
            # Likely a CRS code search
            results = Station.objects.filter(crs_code__iexact=query.upper())
        else:
            results = Station.objects.filter(
                Q(name__icontains=query) | Q(crs_code__icontains=query.upper())
            ).order_by('name')

        # If exactly one result, redirect to station page
        if results.count() == 1:
            return redirect('rail:station_detail', crs=results.first().crs_code)

    context = {
        'query': query,
        'results': results,
        'page_title': f'Search: {query} — UK Rail Live' if query else 'Search — UK Rail Live',
        'meta_description': 'Search for UK railway stations by name or CRS code.',
    }
    return render(request, 'rail/search_results.html', context)


# ── Station data JSON (for map) ──────────────────────────────────────────

@require_GET
def station_geojson(request):
    """Return all stations as GeoJSON for map rendering."""
    stations = Station.objects.all().values('crs_code', 'name', 'lat', 'lon', 'region')
    features = []
    for s in stations:
        features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [s['lon'], s['lat']],
            },
            'properties': {
                'crs': s['crs_code'],
                'name': s['name'],
                'region': s['region'],
            },
        })
    return JsonResponse({
        'type': 'FeatureCollection',
        'features': features,
    })


# ── Error handlers ────────────────────────────────────────────────────────

def custom_404(request, exception=None):
    return render(request, 'rail/404.html', {'page_title': 'Page Not Found — UK Rail Live'}, status=404)


def custom_500(request):
    return render(request, 'rail/500.html', {'page_title': 'Server Error — UK Rail Live'}, status=500)