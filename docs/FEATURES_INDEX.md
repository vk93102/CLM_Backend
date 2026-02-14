# Feature Documentation Index

Each feature has its own Markdown doc. For live request/response shapes, use Swagger UI:

- Swagger UI: `/api/docs/`
- OpenAPI JSON: `/api/schema/`

## How to use Swagger

1. Start the backend.
2. Open `/api/docs/`.
3. Click **Authorize** and paste: `Bearer <access_token>`.

## Environment note (SimpleJWT warning)

If you see a warning about `pkg_resources` being deprecated coming from `rest_framework_simplejwt`, it’s safe to ignore.
To silence it long-term, run the backend using the project venv and keep `setuptools<81` (already pinned in `requirements.txt`).

## Features

- [Authentication](authentication.md)
- [Admin](admin.md)
- [Dashboard](dashboard.md)
- [Contracts](contracts.md)
- [Templates](templates.md)
- [E-Sign: SignNow](esign-signnow.md)
- [E-Sign: Firma](esign-firma.md)
- [Repository & Private Uploads](repository.md)
- [Search](search.md)
- [Notifications](notifications.md)
- [Workflows](workflows.md)
- [Approvals](approvals.md)
- [Reviews](reviews.md)
- [Calendar](calendar.md)
- [AI](ai.md)
- [Health & Metrics](health-metrics.md)
