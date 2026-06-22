"""DRF API views for UK Rail Live."""
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Station, Service, Disruption
from .serializers import StationSerializer, ServiceSerializer, DisruptionSerializer
from .services import get_darwin_client, DarwinAPIError


class StationViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for stations."""
    queryset = Station.objects.all().order_by('name')
    serializer_class = StationSerializer
    lookup_field = 'crs_code'
    search_fields = ['name', 'crs_code']

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.query_params.get('q')
        if q:
            from django.db.models import Q
            queryset = queryset.filter(Q(name__icontains=q) | Q(crs_code__icontains=q.upper()))
        return queryset

    @action(detail=True, methods=['get'])
    def departures(self, request, crs_code=None):
        """Live departures for a station."""
        station = self.get_object()
        try:
            client = get_darwin_client()
            departures = client.get_departures(station.crs_code)
            return Response({'station': station.crs_code, 'departures': departures})
        except DarwinAPIError as e:
            return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    @action(detail=True, methods=['get'])
    def arrivals(self, request, crs_code=None):
        """Live arrivals for a station."""
        station = self.get_object()
        try:
            client = get_darwin_client()
            arrivals = client.get_arrivals(station.crs_code)
            return Response({'station': station.crs_code, 'arrivals': arrivals})
        except DarwinAPIError as e:
            return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class DisruptionViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for disruptions."""
    queryset = Disruption.objects.all().order_by('-start_time')
    serializer_class = DisruptionSerializer
    lookup_field = 'incident_id'

    def get_queryset(self):
        queryset = super().get_queryset()
        active = self.request.query_params.get('active')
        if active and active.lower() in ('true', '1'):
            queryset = queryset.filter(is_active=True)
        return queryset