# AI

## Purpose
AI-related endpoints exposed through the AI viewset.

## Swagger
- Swagger UI: `/api/docs/` (tag: **AI**)
- OpenAPI JSON: `/api/schema/`

## Base path
- `/api/v1/`

## Endpoints (router)
- `/api/v1/ai/`

## Implementation approach

- AI endpoints are exposed via a DRF router ViewSet.
- Some operations may enqueue background work (Celery) depending on configuration.
- Treat Swagger as the source of truth for payloads and response shapes.

## Example request
```bash
curl "$BASE_URL/api/v1/ai/" \
	-H "Authorization: Bearer <access_token>"
```
