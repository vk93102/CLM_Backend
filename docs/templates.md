# Templates

## Purpose
Template type listing, DB-backed template file management, and user template management.

## Swagger
- Swagger UI: `/api/docs/` (tag: **Templates**)
- OpenAPI JSON: `/api/schema/`

## Base path
- `/api/v1/templates/`

## Endpoints
- Template types
  - `GET /api/v1/templates/types/`
  - `GET /api/v1/templates/types/{template_type}/`

- Template files
  - `GET /api/v1/templates/files/`
  - `GET /api/v1/templates/files/mine/`
  - `GET /api/v1/templates/files/schema/{filename}/`
  - `GET /api/v1/templates/files/content/{filename}/`
  - `GET|POST /api/v1/templates/files/signature-fields-config/{filename}/`
  - `POST /api/v1/templates/files/drag-signature-positions/{filename}/`
  - `DELETE|POST /api/v1/templates/files/delete/{filename}/`

- Summary / creation / validation
  - `GET /api/v1/templates/summary/`
  - `POST /api/v1/templates/create-from-type/`
  - `POST /api/v1/templates/validate/`

- User templates
  - `GET /api/v1/templates/user/`
  - `DELETE /api/v1/templates/{template_id}/`

  ## Implementation approach

  - Templates are represented in multiple ways:
    - **TemplateFile**: DB-backed plain-text templates (`contracts.models.TemplateFile`).
    - **ContractTemplate**: versioned templates used in generation flows (`contracts.models.ContractTemplate`).
  - Some template file helpers can import a template from the filesystem into the DB (best-effort) when requested.

  ## Signature fields configuration

  - Signature placement configuration is stored per template file (`signature_fields_config`).
  - Endpoints under `templates/files/signature-fields-config/*` and `templates/files/drag-signature-positions/*` support configuring and adjusting positions.

  ## Example requests

  ### List template types
  ```bash
  curl "$BASE_URL/api/v1/templates/types/" \
    -H "Authorization: Bearer <access_token>"
  ```

  ### Read a template file content
  ```bash
  curl "$BASE_URL/api/v1/templates/files/content/<filename>/" \
    -H "Authorization: Bearer <access_token>"
  ```
