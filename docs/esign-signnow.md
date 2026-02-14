# E-Sign: SignNow

## Purpose
Upload a contract to SignNow, send signing requests, and fetch status/executed documents.

## Swagger
- Swagger UI: `/api/docs/` (tag: **Contracts**; SignNow endpoints live under contracts module)
- OpenAPI JSON: `/api/schema/`

## Base path
- `/api/v1/`

## Endpoints
- `POST /api/v1/contracts/upload/`
- `POST /api/v1/esign/send/`
- `GET /api/v1/esign/signing-url/{contract_id}/`
- `GET /api/v1/esign/status/{contract_id}/`
- `GET /api/v1/esign/executed/{contract_id}/`

## Implementation approach

- These endpoints live under the contracts module and typically:
	- upload a document to the vendor
	- initiate a signing request
	- poll for status
	- download the executed document

## Example requests

### Check status
```bash
curl "$BASE_URL/api/v1/esign/status/<contract_id>/" \
	-H "Authorization: Bearer <access_token>"
```
