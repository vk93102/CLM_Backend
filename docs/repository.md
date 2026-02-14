# Repository & Private Uploads

## Purpose
Document repository CRUD plus R2-backed private uploads used by the app.

## Swagger
- Swagger UI: `/api/docs/` (tag: **Repository**)
- OpenAPI JSON: `/api/schema/`

## Base path
- `/api/v1/`

## Repository endpoints (router)
- `/api/v1/repository/`
- `/api/v1/repository-folders/`
- `/api/v1/documents/`
- `/api/v1/search/` (repository search)

## Private uploads (R2)
- `GET|POST /api/v1/private-uploads/`
- `POST /api/v1/private-uploads/url/`

## Implementation approach

- Repository endpoints are DRF router-based ViewSets (standard CRUD semantics).
- Private uploads are designed for direct-to-storage flows:
	- request an upload URL
	- upload directly to R2
	- list previously uploaded objects

## Example requests

### Create a private upload URL
```bash
curl -X POST "$BASE_URL/api/v1/private-uploads/url/" \
	-H 'Content-Type: application/json' \
	-H "Authorization: Bearer <access_token>" \
	-d '{"filename":"example.pdf","content_type":"application/pdf"}'
```
