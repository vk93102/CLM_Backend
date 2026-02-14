# Calendar

## Purpose
Calendar events for reminders and tracking.

## Swagger
- Swagger UI: `/api/docs/` (tag: **Calendar**)
- OpenAPI JSON: `/api/schema/`

## Base path
- `/api/v1/`

## Endpoints (router)
- `/api/v1/events/`

## Implementation approach

- Calendar events are exposed via a DRF router ViewSet.
- Supports CRUD for reminders/tracking.

## Example request
```bash
curl "$BASE_URL/api/v1/events/" \
	-H "Authorization: Bearer <access_token>"
```
