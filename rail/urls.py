"""URL patterns for the rail app."""
from django.urls import path
from . import views

app_name = 'rail'

urlpatterns = [
    # Homepage
    path('', views.homepage, name='homepage'),

    # Stations
    path('stations/', views.station_list, name='station_list'),
    path('stations/<str:crs>/', views.station_detail, name='station_detail'),
    path('stations/<str:crs>/departures/', views.station_departures_partial, name='station_departures_partial'),
    path('stations/<str:crs>/arrivals/', views.station_arrivals_partial, name='station_arrivals_partial'),

    # Services
    path('services/<str:rid>/', views.service_detail, name='service_detail'),

    # Disruptions
    path('disruptions/', views.disruption_list, name='disruption_list'),
    path('disruptions/<str:incident_id>/', views.disruption_detail, name='disruption_detail'),

    # Map
    path('map/', views.map_view, name='map'),
    path('api/stations/geojson/', views.station_geojson, name='station_geojson'),

    # Search
    path('search/', views.search, name='search'),
]