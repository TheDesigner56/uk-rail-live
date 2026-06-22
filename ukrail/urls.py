"""URL configuration for UK Rail Live."""
from django.contrib import sitemaps
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from rail.sitemaps import StationSitemap, StaticViewSitemap
from rail import views as rail_views

from django.contrib import admin

handler404 = 'rail.views.custom_404'
handler500 = 'rail.views.custom_500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('rail.api_urls')),
    path(
        'sitemap.xml',
        sitemap,
        {'sitemaps': {
            'stations': StationSitemap(),
            'static': StaticViewSitemap(),
        }},
        name='django.contrib.sitemaps.views.sitemap',
    ),
    path('', include('rail.urls')),
]