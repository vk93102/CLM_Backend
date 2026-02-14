# Contracts

## Purpose
Core contract lifecycle APIs: CRUD, generation jobs, approval flow, R2 document operations.

## Swagger
- Swagger UI: `/api/docs/` (tag: **Contracts**)
- OpenAPI JSON: `/api/schema/`

## Base path
- `/api/v1/`

## Main endpoints (router)
- `/api/v1/contracts/` (list/create)
- `/api/v1/contracts/{id}/` (retrieve/update/delete)

## Implementation approach

- Primary ViewSet: `contracts/views.py` → `ContractViewSet` (DRF `ModelViewSet`).
- Tenant isolation: `ContractViewSet.get_queryset()` filters by `tenant_id`.
- User isolation (non-admin): additionally scopes contracts to:
  - contracts created by the user, OR
  - contracts where the user is present in `current_approvers`
- Storage: Cloudflare R2 is used for documents (see `authentication/r2_service.py`).

## Create/update patterns

- List/create is typically `application/json` for metadata and `multipart/form-data` when uploading files.
- Large columns are deferred on list calls for performance.

### Delete contract rules
- Non-admin users can delete only contracts they created.
- Non-admin users cannot delete `status=executed`.
- Deletion performs best-effort Cloudflare R2 cleanup.

## Common status codes
- `200`/`201` success
- `204` deleted
- `400` invalid state (e.g., executed delete blocked)
- `403` permission denied (wrong user)
- `404` not found in tenant scope

## Example requests

### List contracts
```bash
curl "$BASE_URL/api/v1/contracts/" \
  -H "Authorization: Bearer <access_token>"
```

### Delete contract
```bash
curl -X DELETE "$BASE_URL/api/v1/contracts/<contract_uuid>/" \
  -H "Authorization: Bearer <access_token>"
```

## Supporting endpoints
- R2 uploads/download links
  - `POST /api/v1/upload-document/`
  - `POST /api/v1/upload-contract-document/`
  - `POST /api/v1/document-download-url/`
  - `GET /api/v1/{contract_id}/download-url/`

- Generation jobs
  - `/api/v1/generation-jobs/`

## Notes
Contract visibility is tenant-scoped and additionally user-scoped for non-admin users.
