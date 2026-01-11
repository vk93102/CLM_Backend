from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RepositoryViewSet, RepositoryFolderViewSet

router = DefaultRouter()
router.register(r'repository', RepositoryViewSet, basename='repository')
router.register(r'repository-folders', RepositoryFolderViewSet, basename='repository-folder')

urlpatterns = [
    path('', include(router.urls)),
]
