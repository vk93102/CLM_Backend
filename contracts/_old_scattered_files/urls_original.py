"""
URL configuration for contracts app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .generation_views import (
    ContractTemplateViewSet,
    ClauseViewSet,
    ContractViewSet,
    GenerationJobViewSet,
)
from .r2_views import (
    upload_document,
    upload_contract_document,
    get_document_download_url,
    get_contract_download_url,
)

router = DefaultRouter()
router.register(r'contract-templates', ContractTemplateViewSet, basename='contract-template')
router.register(r'clauses', ClauseViewSet, basename='clause')
router.register(r'contracts', ContractViewSet, basename='contract')
router.register(r'generation-jobs', GenerationJobViewSet, basename='generation-job')

urlpatterns = [
    path('', include(router.urls)),
    # Cloudflare R2 upload endpoints (NEW)
    path('upload-document/', upload_document, name='upload-document'),
    path('upload-contract-document/', upload_contract_document, name='upload-contract-document'),
    path('document-download-url/', get_document_download_url, name='document-download-url'),
    path('<uuid:contract_id>/download-url/', get_contract_download_url, name='contract-download-url'),
]
