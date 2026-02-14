# Notifications

## Purpose
User notifications CRUD.

## Swagger
- Swagger UI: `/api/docs/` (tag: **Notifications**)
- OpenAPI JSON: `/api/schema/`

## Base path
- `/api/`

## Endpoints (router)
- `/api/notifications/`
- `/api/notifications/{id}/`

## Implementation approach

- DRF ViewSet-based CRUD under `/api/notifications/`.
- Use `GET` to list, `POST` to create, `PATCH` to update fields, `DELETE` to remove.

## Example requests

### List notifications
```bash
curl "$BASE_URL/api/notifications/" \
	-H "Authorization: Bearer <access_token>"
```
