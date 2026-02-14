# Authentication

## Purpose
Handles user registration/login and returns JWT tokens used for all protected APIs.

## Swagger
- Swagger UI: `/api/docs/` (tag: **Authentication**)
- OpenAPI JSON: `/api/schema/`

## Base path
- `/api/auth/`

## Implementation approach

- **JWT provider**: `rest_framework_simplejwt`.
- **Stateless auth**: the API uses a lightweight user built from JWT claims to avoid a database lookup on every request.
	- Implementation: `authentication/jwt_auth.py` (`StatelessJWTAuthentication`, `JWTClaimsUser`).
- **Claims embedded in tokens** so downstream views can do tenant/user scoping without DB calls:
	- `tenant_id`, `user_id`, `is_admin`, `is_superadmin`.
- **Tenant selection at register**: tenant is resolved from `tenant_id`, `tenant_domain`, email domain, or created as a fallback.
- **OTP flows**: endpoints exist for email verification and password reset via OTP.

## Typical flows

### Register + verify email
1. `POST /api/auth/register/`
2. `POST /api/auth/verify-email-otp/`
3. `POST /api/auth/login/`

### Login + call APIs
1. `POST /api/auth/login/` → store `access` token
2. Call protected endpoints with `Authorization: Bearer <access>`
3. When expired: `POST /api/auth/token/refresh/`

## Endpoints
- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/google/`
- `GET /api/auth/me/`
- `POST /api/auth/token/refresh/`
- `POST /api/auth/forgot-password/`
- `POST /api/auth/reset-password/`
- `POST /api/auth/logout/`
- `POST /api/auth/refresh/`
- `POST /api/auth/verify-password-reset-otp/`
- `POST /api/auth/resend-password-reset-otp/`
- `POST /api/auth/request-login-otp/`
- `POST /api/auth/verify-email-otp/`

## Auth header
All non-auth endpoints expect:

```http
Authorization: Bearer <access_token>
```

## JWT claims
Tokens include:
- `user_id`, `email`, `tenant_id`, `is_admin`, `is_superadmin`

## Common status codes
- `200` success
- `201` created (register)
- `400` validation errors / missing fields
- `401` invalid credentials / invalid token
- `403` account not verified (login may respond with `pending_verification: true`)

## Example requests

### Login
```bash
curl -X POST "$BASE_URL/api/auth/login/" \
	-H 'Content-Type: application/json' \
	-d '{"email":"user@example.com","password":"secret"}'
```

### Refresh token
```bash
curl -X POST "$BASE_URL/api/auth/token/refresh/" \
	-H 'Content-Type: application/json' \
	-d '{"refresh":"<refresh_token>"}'
```

### Me
```bash
curl "$BASE_URL/api/auth/me/" \
	-H "Authorization: Bearer <access_token>"
```
