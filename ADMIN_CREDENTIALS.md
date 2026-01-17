# CLM Backend - Admin Credentials

## Server Information
- **Base URL:** `http://localhost:8000/api`
- **Server Status:** ✅ Running
- **Django Version:** 5.0
- **Database:** PostgreSQL (Supabase)

---

## Admin Accounts

### 1. Primary Admin Account
```
Email: admin@clm.local
Password: admin123
Role: Superuser (Full system access)
Permissions: All permissions
```

### 2. Manager Account
```
Email: manager@clm.local
Password: admin123
Role: Manager (Staff access)
Permissions: Contract management, approvals
```

### 3. Special User Account
```
Email: rahuljha996886@gmail.com
Password: Rahuljha@123
Role: Standard User
```

---

## Quick Test Commands

### Login and Get Token
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@clm.local",
    "password": "admin123"
  }'
```

### Test Admin Dashboard
```bash
TOKEN="your_access_token_here"

curl http://localhost:8000/api/admin/dashboard/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## All Available Endpoints

### Public Endpoints (No Auth Required)
1. `GET /api/roles/` - List all roles with user counts
2. `GET /api/permissions/` - List all system permissions
3. `GET /api/users/` - List all users (paginated)

### Authentication
4. `POST /api/auth/login/` - Login and get JWT token

### Admin Endpoints (Requires Bearer Token)
5. `GET /api/admin/dashboard/` - Dashboard metrics
6. `GET /api/admin/get_users/` - Get all users (paginated)
7. `GET /api/admin/get_roles/` - Get role definitions
8. `GET /api/admin/get_permissions/` - Get permission list
9. `GET /api/admin/get_tenants/` - Get all tenants
10. `GET /api/admin/get_audit_logs/` - Get audit logs (paginated)
11. `GET /api/admin/get_sla_rules/` - Get SLA rules
12. `GET /api/admin/get_sla_breaches/` - Get SLA breaches

---

## Database Statistics (Current)
- **Total Users:** 92
- **Total Contracts:** 57
- **Total Tenants:** 7
- **Admin Users:** 2 (admin@clm.local, manager@clm.local)

---

## Test Script
Run comprehensive test of all endpoints:
```bash
bash QUICK_ENDPOINT_TEST.sh
```

This will test all 11 endpoints and display results with color-coded status indicators.

---

## Notes
- All admin endpoints use AllowAny permission class for development
- All data is fetched from real PostgreSQL database
- Pagination supported: `?limit=X&offset=Y`
- All responses return JSON with `success: true/false`
- Error handling and logging implemented

---

**Last Updated:** January 13, 2026  
**Status:** ✅ All endpoints working and tested
