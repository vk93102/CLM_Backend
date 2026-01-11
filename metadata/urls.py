from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MetadataFieldViewSet

router = DefaultRouter()
router.register(r'metadata/fields', MetadataFieldViewSet, basename='metadata-field')

urlpatterns = [
    path('', include(router.urls)),
]
