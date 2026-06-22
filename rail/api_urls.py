"""API URL configuration for UK Rail Live."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import StationViewSet, DisruptionViewSet

router = DefaultRouter()
router.register(r'stations', StationViewSet, basename='station')
router.register(r'disruptions', DisruptionViewSet, basename='disruption')

urlpatterns = [
    path('', include(router.urls)),
]