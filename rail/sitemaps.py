"""Sitemap configuration for UK Rail Live."""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Station


class StationSitemap(Sitemap):
    """Sitemap for all station pages."""
    changefreq = 'hourly'
    priority = 0.9
    protocol = 'https'

    def items(self):
        return Station.objects.all()

    def location(self, obj):
        return f'/stations/{obj.crs_code.lower()}/'

    def lastmod(self, obj):
        return None


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages."""
    changefreq = 'daily'
    priority = 0.7
    protocol = 'https'

    def items(self):
        return ['rail:homepage', 'rail:station_list', 'rail:disruption_list', 'rail:map']

    def location(self, item):
        return reverse(item)