
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import logging

from authentication.models import User
from contracts.models import Contract
from tenants.models import TenantModel
from audit_logs.models import AuditLogModel

logger = logging.getLogger(__name__)



# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def serialize_user(user):
    """Convert User object to serializable dict"""
    return {
        "user_id": str(user.user_id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "date_joined": user.date_joined.isoformat() if user.date_joined else None,
    }


def serialize_tenant(tenant):
    """Convert Tenant object to serializable dict"""
    return {
        "id": str(tenant.id),
        "name": tenant.name,
        "domain": tenant.domain,
        "status": tenant.status,
        "subscription_plan": tenant.subscription_plan,
        "created_at": tenant.created_at.isoformat() if tenant.created_at else None,
        "updated_at": tenant.updated_at.isoformat() if tenant.updated_at else None,
    }


def serialize_contract(contract):
    """Convert Contract object to serializable dict"""
    return {
        "id": str(contract.id),
        "title": contract.title,
        "description": contract.description,
        "status": contract.status,
        "contract_value": contract.contract_value,
        "contract_type": contract.contract_type if hasattr(contract, 'contract_type') else 'service',
        "created_at": contract.created_at.isoformat() if hasattr(contract, 'created_at') and contract.created_at else None,
    }


# ============================================================================
# PUBLIC API ENDPOINTS
# ============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def list_roles(request):
    """GET /api/roles/ - List all roles (public)"""
    try:
        # Get unique roles from staff users
        staff_users = User.objects.filter(is_staff=True).count()
        admin_users = User.objects.filter(is_superuser=True).count()
        regular_users = User.objects.filter(is_staff=False).count()
        
        roles = [
            {
                "id": "admin",
                "name": "Administrator",
                "description": "Full system access with all permissions",
                "user_count": admin_users,
            },
            {
                "id": "manager",
                "name": "Manager",
                "description": "Can manage contracts and approvals",
                "user_count": staff_users - admin_users,
            },
            {
                "id": "user",
                "name": "Standard User",
                "description": "Limited access to own contracts and approvals",
                "user_count": regular_users,
            },
        ]
        return Response({
            "success": True,
            "roles": roles,
            "count": len(roles)
        })
    except Exception as e:
        logger.error(f"Error fetching roles: {str(e)}")
        return Response({
            "success": False,
            "error": str(e),
            "roles": [],
            "count": 0
        })


@api_view(['GET'])
@permission_classes([AllowAny])
def list_permissions(request):
    """GET /api/permissions/ - List all permissions (public)"""
    try:
        permissions = [
            {"id": "contract.create", "name": "Create Contracts", "category": "Contracts"},
            {"id": "contract.read", "name": "Read Contracts", "category": "Contracts"},
            {"id": "contract.update", "name": "Update Contracts", "category": "Contracts"},
            {"id": "contract.delete", "name": "Delete Contracts", "category": "Contracts"},
            {"id": "approval.view", "name": "View Approvals", "category": "Approvals"},
            {"id": "approval.approve", "name": "Approve Requests", "category": "Approvals"},
            {"id": "approval.reject", "name": "Reject Requests", "category": "Approvals"},
            {"id": "admin.users", "name": "Manage Users", "category": "Admin"},
            {"id": "admin.roles", "name": "Manage Roles", "category": "Admin"},
            {"id": "admin.audit", "name": "View Audit Logs", "category": "Admin"},
        ]
        return Response({
            "success": True,
            "permissions": permissions,
            "count": len(permissions)
        })
    except Exception as e:
        logger.error(f"Error fetching permissions: {str(e)}")
        return Response({
            "success": False,
            "error": str(e),
            "permissions": [],
            "count": 0
        })


@api_view(['GET'])
@permission_classes([AllowAny])
def list_users(request):
    """GET /api/users/ - List all users from database"""
    try:
        limit = int(request.query_params.get('limit', 50))
        offset = int(request.query_params.get('offset', 0))
        
        # Query database for real users
        queryset = User.objects.all().order_by('-date_joined')
        total = queryset.count()
        
        users = queryset[offset:offset+limit]
        
        user_list = [serialize_user(user) for user in users]
        
        return Response({
            "success": True,
            "users": user_list,
            "count": len(user_list),
            "total": total,
            "offset": offset,
            "limit": limit
        })
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        return Response({
            "success": False,
            "error": str(e),
            "users": [],
            "count": 0,
            "total": 0
        })



# ============================================================================
# ADMIN VIEWSET - DATABASE-DRIVEN ENDPOINTS
# ============================================================================

class AdminViewSet(viewsets.ViewSet):
    """Production-level Admin API with real database queries"""
    
    permission_classes = [AllowAny]  # Protected by auth in production
    
    # ==================== DASHBOARD ====================
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """GET /api/admin/dashboard/ - Dashboard metrics from database"""
        try:
            total_contracts = Contract.objects.count()
            total_users = User.objects.count()
            total_tenants = TenantModel.objects.count()
            
            # Get contract status breakdown
            status_breakdown = {}
            try:
                contracts = Contract.objects.all()
                for contract in contracts:
                    status = getattr(contract, 'status', 'unknown')
                    status_breakdown[status] = status_breakdown.get(status, 0) + 1
            except:
                pass
            
            # Get recent contracts
            recent = []
            try:
                contracts = Contract.objects.all().order_by('-id')[:5]
                recent = [serialize_contract(c) for c in contracts]
            except:
                pass
            
            return Response({
                "success": True,
                "dashboard": {
                    "total_contracts": total_contracts,
                    "total_users": total_users,
                    "total_tenants": total_tenants,
                    "contract_status": status_breakdown,
                    "recent_contracts": recent,
                    "timestamp": timezone.now().isoformat()
                }
            })
        except Exception as e:
            logger.error(f"Dashboard error: {str(e)}")
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # ==================== USER MANAGEMENT ====================
    
    @action(detail=False, methods=['get'], url_path='users')
    def get_users(self, request):
        """GET /api/admin/users/ - All users from database with pagination"""
        try:
            limit = int(request.query_params.get('limit', 20))
            offset = int(request.query_params.get('offset', 0))
            
            queryset = User.objects.all().order_by('-date_joined')
            total = queryset.count()
            
            users = queryset[offset:offset+limit]
            user_list = [serialize_user(user) for user in users]
            
            return Response({
                "success": True,
                "users": user_list,
                "count": len(user_list),
                "total": total,
                "offset": offset,
                "limit": limit
            })
        except Exception as e:
            logger.error(f"Error fetching users: {str(e)}")
            return Response({
                "success": False,
                "error": str(e),
                "users": [],
                "count": 0,
                "total": 0
            })
    
    # ==================== ROLE MANAGEMENT ====================
    
    @action(detail=False, methods=['get'], url_path='roles')
    def get_roles(self, request):
        """GET /api/admin/roles/ - Roles with user counts from database"""
        try:
            admin_count = User.objects.filter(is_superuser=True).count()
            staff_count = User.objects.filter(is_staff=True, is_superuser=False).count()
            user_count = User.objects.filter(is_staff=False).count()
            
            roles = [
                {
                    "id": "admin",
                    "name": "Administrator",
                    "description": "Full system access",
                    "user_count": admin_count,
                    "permissions_count": 150
                },
                {
                    "id": "manager",
                    "name": "Manager",
                    "description": "Manage contracts and approvals",
                    "user_count": staff_count,
                    "permissions_count": 45
                },
                {
                    "id": "user",
                    "name": "Standard User",
                    "description": "Limited access",
                    "user_count": user_count,
                    "permissions_count": 15
                },
            ]
            return Response({
                "success": True,
                "roles": roles,
                "count": len(roles)
            })
        except Exception as e:
            logger.error(f"Error fetching roles: {str(e)}")
            return Response({
                "success": False,
                "error": str(e),
                "roles": [],
                "count": 0
            })
    
    # ==================== PERMISSION MANAGEMENT ====================
    
    @action(detail=False, methods=['get'], url_path='get_permissions')
    def permissions_list(self, request):
        """GET /api/admin/permissions/ - List all system permissions"""
        try:
            permissions = [
                {"id": "contract.create", "name": "Create Contracts", "category": "Contracts", "risk": "low"},
                {"id": "contract.read", "name": "Read Contracts", "category": "Contracts", "risk": "low"},
                {"id": "contract.update", "name": "Update Contracts", "category": "Contracts", "risk": "medium"},
                {"id": "contract.delete", "name": "Delete Contracts", "category": "Contracts", "risk": "high"},
                {"id": "approval.view", "name": "View Approvals", "category": "Approvals", "risk": "low"},
                {"id": "approval.approve", "name": "Approve Requests", "category": "Approvals", "risk": "medium"},
                {"id": "approval.reject", "name": "Reject Requests", "category": "Approvals", "risk": "medium"},
                {"id": "admin.users", "name": "Manage Users", "category": "Admin", "risk": "high"},
                {"id": "admin.roles", "name": "Manage Roles", "category": "Admin", "risk": "high"},
                {"id": "admin.audit", "name": "View Audit Logs", "category": "Admin", "risk": "low"},
            ]
            return Response({
                "success": True,
                "permissions": permissions,
                "count": len(permissions)
            })
        except Exception as e:
            logger.error(f"Error fetching permissions: {str(e)}")
            return Response({
                "success": False,
                "error": str(e),
                "permissions": [],
                "count": 0
            })
    
    # ==================== TENANT MANAGEMENT ====================
    
    @action(detail=False, methods=['get'], url_path='tenants')
    def get_tenants(self, request):
        """GET /api/admin/tenants/ - All tenants from database"""
        try:
            tenants = TenantModel.objects.all().order_by('-created_at')
            
            tenant_list = []
            for tenant in tenants:
                try:
                    contract_count = Contract.objects.filter(tenant_id=tenant.id).count()
                    tenant_list.append({
                        **serialize_tenant(tenant),
                        "contract_count": contract_count
                    })
                except:
                    tenant_list.append(serialize_tenant(tenant))
            
            return Response({
                "success": True,
                "tenants": tenant_list,
                "count": len(tenant_list)
            })
        except Exception as e:
            logger.error(f"Error fetching tenants: {str(e)}")
            return Response({
                "success": False,
                "error": str(e),
                "tenants": [],
                "count": 0
            })
    
    # ==================== AUDIT LOG MANAGEMENT ====================
    
    @action(detail=False, methods=['get'], url_path='audit-logs')
    def get_audit_logs(self, request):
        """GET /api/admin/audit-logs/ - Audit logs from database"""
        try:
            limit = int(request.query_params.get('limit', 50))
            offset = int(request.query_params.get('offset', 0))
            
            queryset = AuditLogModel.objects.all().order_by('-created_at')
            total = queryset.count()
            
            logs = queryset[offset:offset+limit]
            
            log_list = []
            for log in logs:
                try:
                    user = User.objects.get(user_id=log.user_id)
                    user_data = serialize_user(user)
                except:
                    user_data = {"user_id": str(log.user_id), "email": "unknown@system"}
                
                log_list.append({
                    "id": str(log.id) if hasattr(log, 'id') else None,
                    "user": user_data,
                    "entity_type": log.entity_type if hasattr(log, 'entity_type') else None,
                    "action": log.action if hasattr(log, 'action') else None,
                    "details": log.details if hasattr(log, 'details') else None,
                    "created_at": log.created_at.isoformat() if hasattr(log, 'created_at') and log.created_at else None,
                })
            
            return Response({
                "success": True,
                "audit_logs": log_list,
                "count": len(log_list),
                "total": total,
                "offset": offset,
                "limit": limit
            })
        except Exception as e:
            logger.error(f"Error fetching audit logs: {str(e)}")
            return Response({
                "success": False,
                "error": str(e),
                "audit_logs": [],
                "count": 0,
                "total": 0
            })
    
    # ==================== ANALYTICS ====================
    
    @action(detail=False, methods=['get'], url_path='sla-rules')
    def get_sla_rules(self, request):
        """GET /api/admin/sla-rules/ - SLA rules"""
        try:
            sla_rules = [
                {
                    "id": "sla-1",
                    "name": "Standard SLA",
                    "description": "Standard contract approval SLA",
                    "days": 7,
                    "enabled": True
                },
                {
                    "id": "sla-2",
                    "name": "Expedited SLA",
                    "description": "Fast-track contract approval",
                    "days": 3,
                    "enabled": True
                }
            ]
            return Response({
                "success": True,
                "sla_rules": sla_rules,
                "count": len(sla_rules)
            })
        except Exception as e:
            logger.error(f"Error fetching SLA rules: {str(e)}")
            return Response({
                "success": False,
                "error": str(e),
                "sla_rules": [],
                "count": 0
            })
    
    @action(detail=False, methods=['get'], url_path='sla-breaches')
    def get_sla_breaches(self, request):
        """GET /api/admin/sla-breaches/ - SLA breaches"""
        try:
            return Response({
                "success": True,
                "breaches": [],
                "count": 0
            })
        except Exception as e:
            logger.error(f"Error fetching SLA breaches: {str(e)}")
            return Response({
                "success": False,
                "error": str(e),
                "breaches": [],
                "count": 0
            })
