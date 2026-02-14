# Approvals

## Purpose
Approval objects and approval flow state.

## Swagger
- Swagger UI: `/api/docs/` (tag: **Approvals**)
- OpenAPI JSON: `/api/schema/`

## Base path
- `/api/v1/`

## Endpoints (router)
- `/api/v1/approvals/`

## Implementation approach

- Approvals are exposed via a DRF router ViewSet.
- Approval decisions typically change server-side state; refer to Swagger for required fields.

## Example requests

### List approvals
```bash
curl "$BASE_URL/api/v1/approvals/" \
	-H "Authorization: Bearer <access_token>"
```
