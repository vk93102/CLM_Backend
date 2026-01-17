from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RepositoryViewSet, RepositoryFolderViewSet
from .document_views import DocumentViewSet
from .search_views import SearchViewSet

router = DefaultRouter()
router.register(r'repository', RepositoryViewSet, basename='repository')
router.register(r'repository-folders', RepositoryFolderViewSet, basename='repository-folder')
router.register(r'documents', DocumentViewSet, basename='documents')
router.register(r'search', SearchViewSet, basename='search')

urlpatterns = [
    path('', include(router.urls)),
]
