"""Admin configuration for UK Rail Live."""
from django.contrib import admin
from .models import Station, Service, Disruption


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('crs_code', 'name', 'region', 'operator', 'lat', 'lon')
    list_filter = ('region',)
    search_fields = ('name', 'crs_code', 'operator')
    ordering = ('name',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('rid', 'origin', 'destination', 'status', 'delay_minutes', 'last_updated')
    list_filter = ('status',)
    search_fields = ('rid', 'uid', 'origin__name', 'destination__name')
    date_hierarchy = 'scheduled_dep'
    ordering = ('-scheduled_dep',)


@admin.register(Disruption)
class DisruptionAdmin(admin.ModelAdmin):
    list_display = ('incident_id', 'type', 'severity', 'is_active', 'start_time')
    list_filter = ('severity', 'is_active', 'type')
    search_fields = ('incident_id', 'summary', 'description')
    date_hierarchy = 'start_time'
    ordering = ('-start_time',)