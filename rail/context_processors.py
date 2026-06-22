"""Context processors for UK Rail Live."""
from django.conf import settings


def ad_slots(request):
    """
    Ad slot context processor — similar to bustimes.org.
    Disable ads on certain pages (errors, admin, etc.)
    """
    path = request.path
    show_ads = True

    # Disable ads on these paths
    no_ad_paths = ['/admin/', '/api/', '/500', '/404']
    for prefix in no_ad_paths:
        if path.startswith(prefix):
            show_ads = False
            break

    return {
        'show_ads': show_ads,
        'ad_slot_top': show_ads,
        'ad_slot_bottom': show_ads,
        'ad_slot_sidebar': show_ads,
    }


def station_count(request):
    """Total station count for footer/display."""
    from .models import Station
    try:
        count = Station.objects.count()
    except Exception:
        count = 0
    return {'total_station_count': count}