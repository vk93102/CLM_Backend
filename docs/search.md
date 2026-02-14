# Search

## Purpose
Full-text, semantic, hybrid, and advanced search used by the frontend.

## Swagger
- Swagger UI: `/api/docs/` (tag: **Search**)
- OpenAPI JSON: `/api/schema/`

## Base path
- `/api/search/`

## Endpoints
- `GET /api/search/?q=<query>`
- `GET /api/search/semantic/?q=<query>`
- `POST /api/search/hybrid/`
- `POST /api/search/advanced/`
- `GET /api/search/facets/`
- `POST /api/search/faceted/`
- `GET /api/search/suggestions/?q=<query>`
- `GET|POST|DELETE /api/search/index/`
- `GET /api/search/analytics/`
- `GET|POST /api/search/similar/`

## Implementation approach

- Keyword search: classic query parameter based (`?q=`).
- Semantic/hybrid search: uses embeddings and similarity search where available.
- Advanced search: accepts structured filters in the request body.

Because search schemas evolve quickly, treat Swagger (`/api/docs/`) as the source of truth for request/response shapes.

## Example requests

### Keyword search
```bash
curl "$BASE_URL/api/search/?q=nda" \
	-H "Authorization: Bearer <access_token>"
```

### Advanced search
```bash
curl -X POST "$BASE_URL/api/search/advanced/" \
	-H 'Content-Type: application/json' \
	-H "Authorization: Bearer <access_token>" \
	-d '{"query":"nda","filters":{}}'
```
