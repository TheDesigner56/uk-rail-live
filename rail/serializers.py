"""DRF serializers for UK Rail Live."""
from rest_framework import serializers
from .models import Station, Service, Disruption


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ['id', 'crs_code', 'name', 'full_name', 'lat', 'lon', 'region', 'operator']


class ServiceSerializer(serializers.ModelSerializer):
    origin_name = serializers.CharField(source='origin.name', read_only=True)
    destination_name = serializers.CharField(source='destination.name', read_only=True)
    origin_crs = serializers.CharField(source='origin.crs_code', read_only=True)
    destination_crs = serializers.CharField(source='destination.crs_code', read_only=True)

    class Meta:
        model = Service
        fields = [
            'id', 'rid', 'uid', 'operator', 'origin_crs', 'origin_name',
            'destination_crs', 'destination_name', 'platform',
            'scheduled_dep', 'estimated_dep', 'actual_dep',
            'scheduled_arr', 'estimated_arr', 'actual_arr',
            'delay_minutes', 'status', 'cancel_reason', 'last_updated',
        ]


class DisruptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disruption
        fields = [
            'id', 'incident_id', 'type', 'summary', 'description',
            'start_time', 'end_time', 'affected_routes', 'severity', 'is_active',
            'created_at', 'updated_at',
        ]