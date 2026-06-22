# UK Rail Live

Real-time UK train departure, arrival, and disruption tracker — built with Django, HTMX, and MapLibre GL.

## Features

- **Live departure & arrival boards** for every UK railway station
- **Auto-refresh** every 60 seconds via HTMX (no page reload)
- **Service detail** tracking for individual trains
- **Network-wide disruption feed** with severity levels
- **Interactive map** of all UK stations (MapLibre GL + OpenStreetMap)
- **Search** by station name or CRS code
- **SEO-optimised** station pages with structured data, sitemap.xml, meta tags
- **Dark mode** with system theme detection and toggle
- **Mobile-first** responsive design (88% mobile traffic)
- **Sub-200ms TTFB** target with caching and lightweight pages
- **REST API** via Django REST Framework
- **Vercel-ready** serverless deployment

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Django 5.x (Python 3.12+) |
| Database | PostgreSQL + PostGIS (Neon) / SpatiaLite (local) |
| Frontend | HTMX + vanilla JS |
| Maps | MapLibre GL JS |
| Static | Whitenoise (compressed) |
| API | National Rail Darwin RTI API |
| Deployment | Vercel serverless |

## Quick Start

### 1. Clone and install

```bash
cd ~/Projects/uk-rail-live
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment variables

```bash
cp .env.example .env
# Edit .env with your settings
```

You'll need:
- `SECRET_KEY` — a random 50-character string
- `DARWIN_API_KEY` — get a free key from [raildata.org.uk](https://raildata.org.uk)
- `DATABASE_URL` — leave empty for local SQLite/SpatiaLite

### 3. Set up database

```bash
python manage.py migrate
python manage.py import_stations --extended  # Import 30 stations
```

### 4. Run dev server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000`

## API Key Setup

1. Go to [raildata.org.uk](https://raildata.org.uk)
2. Register for a free account
3. Subscribe to the **Darwin RTI** (Real-Time Information) API
4. Copy your API key
5. Add to `.env`: `DARWIN_API_KEY=your-key-here`

Without an API key, the app still works — station pages show seed data and static info. Live departures/arrivals will show an error banner.

## Deployment to Vercel

### Prerequisites
- A [Neon](https://neon.tech) Postgres database with PostGIS enabled
- A Darwin API key from raildata.org.uk

### Steps

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variables in Vercel dashboard:
# - SECRET_KEY
# - DATABASE_URL (Neon Postgres URL)
# - DARWIN_API_KEY
# - DEBUG=False
# - ALLOWED_HOSTS=your-domain.vercel.app
```

The `vercel.json` is pre-configured for Django serverless deployment.

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/stations/` | All stations (paginated) |
| `GET /api/stations/{crs}/` | Single station detail |
| `GET /api/stations/{crs}/departures/` | Live departures |
| `GET /api/stations/{crs}/arrivals/` | Live arrivals |
| `GET /api/stations/?q=paddington` | Search stations |
| `GET /api/disruptions/` | All disruptions |
| `GET /api/disruptions/?active=true` | Active disruptions only |
| `GET /api/disruptions/{incident_id}/` | Single disruption |
| `GET /sitemap.xml` | XML sitemap |

## Management Commands

```bash
# Import station data (10 major stations)
python manage.py import_stations

# Import extended station list (30 stations)
python manage.py import_stations --extended

# Clear and re-import
python manage.py import_stations --extended --clear

# Fetch live disruptions from Darwin API
python manage.py fetch_disruptions

# Clear existing before fetching
python manage.py fetch_disruptions --clear
```

## URL Structure

| URL | Description |
|-----|-------------|
| `/` | Homepage (search + map + live disruptions) |
| `/stations/` | All stations list |
| `/stations/{crs}/` | Station page (departures + arrivals) |
| `/services/{rid}/` | Individual service detail |
| `/disruptions/` | Network disruption feed |
| `/disruptions/{incident_id}/` | Individual disruption |
| `/map/` | Full-screen station map |
| `/search/?q=` | Search results |
| `/api/` | REST API |
| `/sitemap.xml` | XML sitemap |

## Project Structure

```
uk-rail-live/
├── manage.py
├── requirements.txt
├── vercel.json
├── .env.example
├── .gitignore
├── README.md
├── ukrail/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── rail/
    ├── __init__.py
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── admin.py
    ├── api.py
    ├── api_urls.py
    ├── serializers.py
    ├── services.py        # Darwin API client
    ├── sitemaps.py
    ├── context_processors.py
    ├── migrations/
    ├── management/
    │   ├── __init__.py
    │   └── commands/
    │       ├── __init__.py
    │       ├── import_stations.py
    │       └── fetch_disruptions.py
    ├── static/
    │   └── rail/
    │       ├── css/style.css
    │       └── js/main.js
    └── templates/
        └── rail/
            ├── base.html
            ├── homepage.html
            ├── station_detail.html
            ├── station_list.html
            ├── service_detail.html
            ├── disruption_list.html
            ├── disruption_detail.html
            ├── map.html
            ├── search_results.html
            ├── 404.html
            ├── 500.html
            └── partials/
                ├── _departures.html
                └── _arrivals.html
```

## Design Notes

- **Dark background** (#0A0A0A) with light text — easy on the eyes for regular commuters
- **Monospace** (JetBrains Mono) for times and platform numbers — scannable departure board aesthetic
- **Inter** for all other text — clean, modern, highly legible
- **No heavy frameworks** — pure CSS + HTMX + vanilla JS for sub-200ms loads
- **Colour coding**: green = on time, amber = delayed, red = cancelled

## License

MIT

## Data Source

Powered by [National Rail Darwin RTI API](https://raildata.org.uk) — real-time train information for the UK rail network.