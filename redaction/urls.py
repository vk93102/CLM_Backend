from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RedactionViewSet

router = DefaultRouter()
router.register(r'redaction', RedactionViewSet, basename='redaction')

urlpatterns = [
    path('', include(router.urls)),
]
