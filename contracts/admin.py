from django.contrib import admin
from . import models
from clm_backend.admin_site import admin_site

# Register models only if they exist (avoids import issues)
if hasattr(models, 'ContractTemplate'):
    @admin.register(models.ContractTemplate, site=admin_site)
    class ContractTemplateAdmin(admin.ModelAdmin):
        list_display = ('name', 'contract_type', 'version', 'status')
        list_filter = ('contract_type', 'status')
        search_fields = ('name', 'contract_type')

if hasattr(models, 'Clause'):
    @admin.register(models.Clause, site=admin_site)
    class ClauseAdmin(admin.ModelAdmin):
        list_display = ('clause_id', 'name', 'contract_type', 'version', 'status')
        list_filter = ('contract_type', 'status', 'is_mandatory')
        search_fields = ('clause_id', 'name')

if hasattr(models, 'Contract'):
    @admin.register(models.Contract, site=admin_site)
    class ContractAdmin(admin.ModelAdmin):
        list_display = ('title', 'contract_type', 'status')
        list_filter = ('status', 'contract_type')
        search_fields = ('title', 'contract_type')

if hasattr(models, 'BusinessRule'):
    @admin.register(models.BusinessRule, site=admin_site)
    class BusinessRuleAdmin(admin.ModelAdmin):
        list_display = ('name', 'rule_type', 'is_active')
        list_filter = ('rule_type', 'is_active')
        search_fields = ('name', 'description')

if hasattr(models, 'TemplateFile'):
    @admin.register(models.TemplateFile, site=admin_site)
    class TemplateFileAdmin(admin.ModelAdmin):
        list_display = ('filename', 'name', 'contract_type', 'status', 'tenant_id', 'updated_at')
        list_filter = ('status', 'contract_type')
        search_fields = ('filename', 'name', 'description')
