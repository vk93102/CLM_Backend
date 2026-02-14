# E-Sign: Firma

## Purpose
Firma e-sign flow: create/upload/send signing requests, webhooks, status/executed docs, and local signing-request tracking.

## Swagger
- Swagger UI: `/api/docs/` (tag: **Firma E-Sign**)
- OpenAPI JSON: `/api/schema/`

## Base path
- `/api/v1/firma/`

## Endpoints
- Core flow
  - `POST /api/v1/firma/sign/`
  - `POST /api/v1/firma/contracts/upload/`
  - `POST /api/v1/firma/esign/send/`
  - `POST /api/v1/firma/esign/invite-all/`

- Requests
  - `GET /api/v1/firma/esign/requests/`
  - `DELETE /api/v1/firma/esign/requests/{record_id}/`
    - Deletes only the local tracking record (`FirmaSignatureContract`)

## Tenant/user scoping and permissions

- All endpoints require authentication unless explicitly documented otherwise (vendor callbacks).
- Requests are tenant-scoped.
- Deleting a signing request:
  - Non-admins may only delete requests for contracts they created.
  - Completed requests are blocked.

- Status / docs
  - `GET /api/v1/firma/esign/signing-url/{contract_id}/`
  - `GET /api/v1/firma/esign/status/{contract_id}/`
  - `GET /api/v1/firma/esign/executed/{contract_id}/`
  - `GET /api/v1/firma/esign/certificate/{contract_id}/`

- Details / reminders / activity
  - `GET /api/v1/firma/esign/details/{contract_id}/`
  - `GET /api/v1/firma/esign/reminders/{contract_id}/`
  - `GET /api/v1/firma/esign/activity/{contract_id}/`
  - `POST /api/v1/firma/esign/resend/{contract_id}/`

- Webhooks
  - `GET|POST /api/v1/firma/webhooks/`
  - `GET|DELETE /api/v1/firma/webhooks/{webhook_id}/`
  - `GET /api/v1/firma/webhooks/secret-status/`
  - `POST /api/v1/firma/webhooks/receive/` (vendor callback)
  - `GET /api/v1/firma/webhooks/stream/{contract_id}/` (authenticated stream)

- JWT helpers
  - `POST /api/v1/firma/jwt/template/generate/`
  - `POST /api/v1/firma/jwt/template/revoke/`
  - `POST /api/v1/firma/jwt/signing-request/generate/`
  - `POST /api/v1/firma/jwt/signing-request/revoke/`

- Debug
  - `GET /api/v1/firma/debug/config/`
  - `GET /api/v1/firma/debug/connectivity/`

## Example requests

### List signing requests
```bash
curl "$BASE_URL/api/v1/firma/esign/requests/" \
  -H "Authorization: Bearer <access_token>"
```

### Delete signing request (local tracking record)
```bash
curl -X DELETE "$BASE_URL/api/v1/firma/esign/requests/<record_uuid>/" \
  -H "Authorization: Bearer <access_token>"
```
