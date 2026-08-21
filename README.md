# Vehicle Availability

A Python-backed vehicle availability and reservation-assignment prototype. The browser UI loads its reservations and vehicle recommendations from a small local JSON API; the included records are dummy data for demos and development.

## Run locally

```bash
python3 server.py
```

Open [http://localhost:8000](http://localhost:8000). No packages need to be installed.

## Dummy data and API

The prototype data is stored in `data/dummy_data.json` and includes five reservations and five vehicles covering ready, equipment-gap, substitution, blocked, and stale-card scenarios.

- `GET /api/reservations` — reservation queue
- `GET /api/vehicles?reservation_id=RA-10482` — ranked vehicle shortlist
- `POST /api/assignments` — confirms an assignment in the server's in-memory demo state
- `GET /api/health` — health check
