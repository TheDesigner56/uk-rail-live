"""Models for UK Rail Live."""
from django.db import models
from django.conf import settings

# Use GIS PointField if available, otherwise skip
if "django.contrib.gis" in settings.INSTALLED_APPS:
    from django.contrib.gis.db.models import PointField
else:
    PointField = None


class Station(models.Model):
    """A UK railway station identified by its CRS code."""

    crs_code = models.CharField(max_length=3, unique=True, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    full_name = models.CharField(max_length=300, blank=True)
    lat = models.FloatField()
    lon = models.FloatField()
    location = PointField(srid=4326, null=True, blank=True) if PointField else None
    region = models.CharField(max_length=100, blank=True)
    operator = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.crs_code})"

    def save(self, *args, **kwargs):
        if self.lat and self.lon and PointField:
            from django.contrib.gis.geos import Point
            self.location = Point(self.lon, self.lat, srid=4326)
        super().save(*args, **kwargs)


class Service(models.Model):
    """A live train service tracked by its RID (Running Identifier)."""

    STATUS_CHOICES = [
        ('on_time', 'On Time'),
        ('delayed', 'Delayed'),
        ('cancelled', 'Cancelled'),
        ('arrived', 'Arrived'),
        ('departed', 'Departed'),
        ('unknown', 'Unknown'),
    ]

    rid = models.CharField(max_length=20, unique=True, db_index=True)
    uid = models.CharField(max_length=10, blank=True)
    operator = models.CharField(max_length=200, blank=True)
    origin = models.ForeignKey(
        Station, related_name='origin_services', on_delete=models.CASCADE
    )
    destination = models.ForeignKey(
        Station, related_name='destination_services', on_delete=models.CASCADE
    )
    platform = models.CharField(max_length=5, blank=True)
    scheduled_dep = models.DateTimeField(null=True, blank=True)
    estimated_dep = models.DateTimeField(null=True, blank=True)
    actual_dep = models.DateTimeField(null=True, blank=True)
    scheduled_arr = models.DateTimeField(null=True, blank=True)
    estimated_arr = models.DateTimeField(null=True, blank=True)
    actual_arr = models.DateTimeField(null=True, blank=True)
    delay_minutes = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unknown')
    cancel_reason = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_dep']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['scheduled_dep']),
        ]

    def __str__(self):
        return f"{self.rid}: {self.origin} → {self.destination}"

    @property
    def is_delayed(self):
        return self.delay_minutes > 5

    @property
    def status_colour(self):
        mapping = {
            'on_time': '#22c55e',
            'delayed': '#f59e0b',
            'cancelled': '#ef4444',
            'arrived': '#3b82f6',
            'departed': '#3b82f6',
            'unknown': '#6b7280',
        }
        return mapping.get(self.status, '#6b7280')


class Disruption(models.Model):
    """A network-wide disruption incident."""

    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('severe', 'Severe'),
    ]

    incident_id = models.CharField(max_length=50, unique=True, db_index=True)
    type = models.CharField(max_length=100)
    summary = models.CharField(max_length=500)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    affected_routes = models.TextField(blank=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['is_active', '-start_time']),
            models.Index(fields=['severity']),
        ]

    def __str__(self):
        return f"{self.incident_id}: {self.summary}"

    @property
    def severity_colour(self):
        mapping = {
            'low': '#22c55e',
            'medium': '#f59e0b',
            'high': '#ef4444',
            'severe': '#7c2d12',
        }
        return mapping.get(self.severity, '#6b7280')