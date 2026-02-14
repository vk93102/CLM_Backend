# Admin

## Purpose
Admin-only analytics and user management APIs.

## Swagger
- Swagger UI: `/api/docs/` (tag: **Admin**)
- OpenAPI JSON: `/api/schema/`

## Base path
- `/api/v1/admin/`

## Endpoints
- `GET /api/v1/admin/me/`
- `GET /api/v1/admin/users/?q=<search>&all_tenants=1|0`
- `POST /api/v1/admin/users/promote/?all_tenants=1|0`
- `POST /api/v1/admin/users/demote/?all_tenants=1|0`
- `GET /api/v1/admin/analytics/`
- `GET /api/v1/admin/activity/`
- `GET /api/v1/admin/feature-usage/`
- `GET /api/v1/admin/user-registration/`
- `GET /api/v1/admin/user-feature-usage/`

## Permissions
- Admin: `is_admin` claim or Django `is_staff/is_superuser`
- Some endpoints require Superadmin: `is_superadmin` claim or `is_superuser`

## Implementation approach

- Views: `authentication/admin_views.py`
- Permission classes: `authentication/permissions.py`
- Data scope:
	- Default is **tenant-scoped** via `request.user.tenant_id`.
	- Some list endpoints support `?all_tenants=1` for superadmins.

## Notes

- When a user is promoted/demoted, they must **re-login** to get updated `is_admin/is_superadmin` claims in their JWT.

## Example requests

### List users
```bash
curl "$BASE_URL/api/v1/admin/users/?q=rahul" \
	-H "Authorization: Bearer <access_token>"
```

### Promote user (superadmin)
```bash
curl -X POST "$BASE_URL/api/v1/admin/users/promote/" \
	-H 'Content-Type: application/json' \
	-H "Authorization: Bearer <access_token>" \
	-d '{"email":"someone@example.com"}'
```
