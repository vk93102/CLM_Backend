# Health & Metrics

## Purpose
Operational endpoints used for uptime checks and metrics scraping.

## Swagger
- Swagger UI: `/api/docs/` (schema is exposed here)
- OpenAPI JSON: `/api/schema/`

## Endpoints
- Health
  - `GET /api/v1/health/`

- Metrics (Prometheus)
  - `GET /metrics`
  - If `METRICS_TOKEN` is set, include header `X-Metrics-Token: <token>`

## Notes
Swagger endpoints:
- `GET /api/schema/`
- `GET /api/docs/`

## Implementation approach

- `/api/v1/health/` is served by the contracts module health view.
- `/metrics` is a Prometheus scrape endpoint and can be optionally protected by `METRICS_TOKEN`.
