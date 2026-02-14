# Workflows

## Purpose
Workflow definitions and workflow instances.

## Swagger
- Swagger UI: `/api/docs/` (tag: **Workflows**)
- OpenAPI JSON: `/api/schema/`

## Base path
- `/api/v1/`

## Endpoints (router)
- `/api/v1/workflows/`
- `/api/v1/workflow-instances/`

## Implementation approach

- Workflow definitions and instances are exposed via DRF router ViewSets.
- Use standard REST semantics:
	- `GET` list/retrieve
	- `POST` create
	- `PATCH` update
	- `DELETE` delete

## Example requests

### List workflows
```bash
curl "$BASE_URL/api/v1/workflows/" \
	-H "Authorization: Bearer <access_token>"
```
