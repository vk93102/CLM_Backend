"""
URL configuration for contracts app - Consolidated
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .template_views import (
    TemplateTypesView,
    TemplateTypeSummaryView,
    TemplateTypeDetailView,
    CreateTemplateFromTypeView,
    ValidateTemplateDataView
)
from .pdf_views import (
    ContractPDFDownloadView,
    ContractBatchPDFGenerationView,
    PDFGenerationStatusView
)

router = DefaultRouter()
router.register(r'contract-templates', views.ContractTemplateViewSet, basename='contract-template')
router.register(r'clauses', views.ClauseViewSet, basename='clause')
router.register(r'contracts', views.ContractViewSet, basename='contract')
router.register(r'generation-jobs', views.GenerationJobViewSet, basename='generation-job')

urlpatterns = [
    path('', include(router.urls)),
    
    # ========== TEMPLATE MANAGEMENT ENDPOINTS ==========
    path('templates/types/', TemplateTypesView.as_view(), name='template-types'),
    path('templates/types/<str:template_type>/', TemplateTypeDetailView.as_view(), name='template-type-detail'),
    path('templates/summary/', TemplateTypeSummaryView.as_view(), name='template-summary'),
    path('templates/create-from-type/', CreateTemplateFromTypeView.as_view(), name='create-template-from-type'),
    path('templates/validate/', ValidateTemplateDataView.as_view(), name='validate-template-data'),
    
    # ========== PDF GENERATION ENDPOINTS ==========
    path('<uuid:template_id>/download-pdf/', ContractPDFDownloadView.as_view(), name='contract-pdf-download'),
    path('batch-generate-pdf/', ContractBatchPDFGenerationView.as_view(), name='batch-pdf-generation'),
    path('pdf-generation-status/', PDFGenerationStatusView.as_view(), name='pdf-generation-status'),
    
    # ========== CLOUDFLARE R2 UPLOAD ENDPOINTS ==========
    path('upload-document/', views.upload_document, name='upload-document'),
    path('upload-contract-document/', views.upload_contract_document, name='upload-contract-document'),
    path('document-download-url/', views.get_document_download_url, name='document-download-url'),
    path('<uuid:contract_id>/download-url/', views.get_contract_download_url, name='contract-download-url'),
    
    # ========== SIGNNOW E-SIGNATURE ENDPOINTS ==========
    path('contracts/upload/', views.upload_contract, name='upload_contract'),
    path('esign/send/', views.send_for_signature, name='send_for_signature'),
    path('esign/signing-url/<str:contract_id>/', views.get_signing_url, name='get_signing_url'),
    path('esign/status/<str:contract_id>/', views.check_status, name='check_status'),
    path('esign/executed/<str:contract_id>/', views.get_executed_document, name='get_executed_document'),
    
    # ========== HEALTH CHECK ENDPOINT ==========
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
]

