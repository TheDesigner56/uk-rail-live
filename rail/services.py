"""
Darwin API client for UK Rail Live.

Connects to the National Rail Darwin Real-Time Information (RTI) API
to fetch live departures, arrivals, and service details.

Register for an API key at https://raildata.org.uk
"""
import logging
import requests
from datetime import datetime, timedelta
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)

# Cache TTL in seconds — Darwin data updates every 30-60 seconds
CACHE_TTL = 60


class DarwinAPIError(Exception):
    """Raised when the Darwin API returns an error."""

    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code


class DarwinClient:
    """Client for the National Rail Darwin RTI API."""

    def __init__(self, api_key=None, base_url=None):
        self.api_key = api_key or ''
        self.base_url = base_url or 'https://api1.raildata.org.uk/1010-knowledge1_1-rti'
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({
                'x-apikey': self.api_key,
                'Accept': 'application/json',
            })

    # ── Public methods ───────────────────────────────────────────────────

    def get_departures(self, crs, num_rows=15):
        """Get live departures at a station by CRS code."""
        cache_key = f'departures:{crs}:{num_rows}'
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        data = self._request('/GetDepBoardWithDetails', {
            'crs': crs.upper(),
            'numRows': num_rows,
        })

        departures = self._parse_departures(data, crs)
        cache.set(cache_key, departures, CACHE_TTL)
        return departures

    def get_arrivals(self, crs, num_rows=15):
        """Get live arrivals at a station by CRS code."""
        cache_key = f'arrivals:{crs}:{num_rows}'
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        data = self._request('/GetArrBoardWithDetails', {
            'crs': crs.upper(),
            'numRows': num_rows,
        })

        arrivals = self._parse_arrivals(data, crs)
        cache.set(cache_key, arrivals, CACHE_TTL)
        return arrivals

    def get_service(self, rid):
        """Get detailed information for a specific service by RID."""
        cache_key = f'service:{rid}'
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        data = self._request('/GetServiceDetails', {
            'rid': rid,
        })

        service = self._parse_service(data)
        cache.set(cache_key, service, CACHE_TTL)
        return service

    def get_disruptions(self):
        """Fetch current network-wide disruptions."""
        cache_key = 'disruptions'
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        data = self._request('/GetDisruptionList', {})
        disruptions = self._parse_disruptions(data)
        cache.set(cache_key, disruptions, CACHE_TTL * 5)  # 5 min for disruptions
        return disruptions

    # ── Private helpers ──────────────────────────────────────────────────

    def _request(self, endpoint, params):
        """Make an authenticated request to the Darwin API."""
        if not self.api_key:
            logger.warning('Darwin API key not configured — returning empty data')
            return {}

        url = f'{self.base_url}{endpoint}'
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error('Darwin API timeout for %s', endpoint)
            raise DarwinAPIError('Darwin API request timed out', 504)
        except requests.exceptions.HTTPError as e:
            logger.error('Darwin API HTTP error: %s', e)
            raise DarwinAPIError(f'Darwin API error: {e}', e.response.status_code)
        except requests.exceptions.RequestException as e:
            logger.error('Darwin API connection error: %s', e)
            raise DarwinAPIError(f'Connection error: {e}')

    def _parse_departures(self, data, crs):
        """Parse the departures board response into service dicts."""
        services = []
        train_services = data.get('trainServices', [])

        for svc in train_services:
            std = svc.get('std', '')
            etd = svc.get('etd', 'On time')
            platform = svc.get('platform', '')
            operator = svc.get('operator', '')
            dest_list = svc.get('destination', {})
            if isinstance(dest_list, list):
                dest_list = dest_list[0] if dest_list else {}
            destination = dest_list.get('locationName', '')
            dest_crs = dest_list.get('crs', '')
            rid = svc.get('rid', '')
            uid = svc.get('uid', '')
            cancel_reason = svc.get('cancelReason', '')

            is_cancelled = etd == 'Cancelled'
            is_delayed = etd not in ('On time', 'Cancelled', 'On Time', '')

            delay_minutes = 0
            if is_delayed and etd.isdigit():
                try:
                    scheduled_dt = self._parse_time(std)
                    estimated_dt = self._parse_time(etd)
                    if scheduled_dt and estimated_dt:
                        delay_minutes = int((estimated_dt - scheduled_dt).total_seconds() / 60)
                except Exception:
                    pass

            services.append({
                'rid': rid,
                'uid': uid,
                'scheduled': std,
                'estimated': etd,
                'platform': platform,
                'operator': operator,
                'destination': destination,
                'dest_crs': dest_crs,
                'origin_crs': crs,
                'is_cancelled': is_cancelled,
                'is_delayed': is_delayed,
                'delay_minutes': max(delay_minutes, 0),
                'cancel_reason': cancel_reason,
            })

        return services

    def _parse_arrivals(self, data, crs):
        """Parse the arrivals board response into service dicts."""
        services = []
        train_services = data.get('trainServices', [])

        for svc in train_services:
            sta = svc.get('sta', '')
            eta = svc.get('eta', 'On time')
            platform = svc.get('platform', '')
            operator = svc.get('operator', '')
            origin_list = svc.get('origin', {})
            if isinstance(origin_list, list):
                origin_list = origin_list[0] if origin_list else {}
            origin = origin_list.get('locationName', '')
            origin_crs = origin_list.get('crs', '')
            rid = svc.get('rid', '')
            uid = svc.get('uid', '')
            cancel_reason = svc.get('cancelReason', '')

            is_cancelled = eta == 'Cancelled'
            is_delayed = eta not in ('On time', 'Cancelled', 'On Time', '')

            services.append({
                'rid': rid,
                'uid': uid,
                'scheduled': sta,
                'estimated': eta,
                'platform': platform,
                'operator': operator,
                'origin': origin,
                'origin_crs': origin_crs,
                'dest_crs': crs,
                'is_cancelled': is_cancelled,
                'is_delayed': is_delayed,
                'cancel_reason': cancel_reason,
            })

        return services

    def _parse_service(self, data):
        """Parse a service detail response."""
        service = data.get('serviceDetails', data)
        return {
            'rid': service.get('rid', ''),
            'uid': service.get('uid', ''),
            'operator': service.get('operator', ''),
            'origin': service.get('origin', ''),
            'destination': service.get('destination', ''),
            'platform': service.get('platform', ''),
            'std': service.get('std', ''),
            'etd': service.get('etd', ''),
            'sta': service.get('sta', ''),
            'eta': service.get('eta', ''),
            'ata': service.get('ata', ''),
            'atd': service.get('atd', ''),
            'cancel_reason': service.get('cancelReason', ''),
            'delay_reason': service.get('delayReason', ''),
            'calling_points': service.get('callingPoints', []),
        }

    def _parse_disruptions(self, data):
        """Parse the disruption feed response."""
        disruptions = []
        incidents = data.get('incidents', [])

        for inc in incidents:
            disruptions.append({
                'incident_id': inc.get('incidentId', ''),
                'type': inc.get('incidentType', ''),
                'summary': inc.get('summary', ''),
                'description': inc.get('description', ''),
                'start_time': inc.get('startTime', ''),
                'end_time': inc.get('endTime', ''),
                'affected_routes': inc.get('affectedRoutes', ''),
                'severity': inc.get('severity', 'medium'),
            })

        return disruptions

    @staticmethod
    def _parse_time(time_str):
        """Parse HH:MM time string into a datetime (today)."""
        if not time_str or time_str in ('On time', 'Cancelled', ''):
            return None
        try:
            now = timezone.now()
            parts = time_str.split(':')
            if len(parts) == 2:
                return now.replace(hour=int(parts[0]), minute=int(parts[1]), second=0, microsecond=0)
        except (ValueError, IndexError):
            pass
        return None


# Singleton accessor
_client = None


def get_darwin_client():
    """Get a shared DarwinClient instance."""
    global _client
    if _client is None:
        from django.conf import settings
        _client = DarwinClient(
            api_key=settings.DARWIN_API_KEY,
            base_url=settings.DARWIN_API_URL,
        )
    return _client