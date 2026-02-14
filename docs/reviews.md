# Reviews

## Purpose
Contract review flows and clause library.

## Swagger
- Swagger UI: `/api/docs/` (tag: **Reviews**)
- OpenAPI JSON: `/api/schema/`

## Base path
- `/api/v1/`

## Endpoints (router)
- `/api/v1/review-contracts/`
- `/api/v1/clause-library/`

## Implementation approach

- Reviews are exposed via DRF router ViewSets.
- A typical review flow:
	- create/upload a review object
	- process/analyze
	- fetch results

Refer to Swagger for exact payload fields.

## Example requests

### List review contracts
```bash
curl "$BASE_URL/api/v1/review-contracts/" \
	-H "Authorization: Bearer <access_token>"
```
