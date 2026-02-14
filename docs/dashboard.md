# Dashboard

## Purpose
Tenant-scoped, per-user KPIs and insights used by the frontend dashboard.

## Swagger
- Swagger UI: `/api/docs/` (tag: **Dashboard**)
- OpenAPI JSON: `/api/schema/`

## Base path
- `/api/v1/dashboard/`

## Endpoints
- `GET /api/v1/dashboard/insights/`

## Implementation approach

- View: `authentication/dashboard_views.py`
- Uses a mix of:
	- Database counts (contracts, reviews, events, templates, audit logs)
	- Best-effort R2 object counting for upload-related metrics
- Tenant/user scoping:
	- Requires `tenant_id` and `user_id` in JWT claims
	- Filters most KPIs to the current user’s activity in the current tenant

## Example request
```bash
curl "$BASE_URL/api/v1/dashboard/insights/" \
	-H "Authorization: Bearer <access_token>"
```
