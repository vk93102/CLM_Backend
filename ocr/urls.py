from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OCRViewSet

router = DefaultRouter()
router.register(r'ocr', OCRViewSet, basename='ocr')

urlpatterns = [
    path('', include(router.urls)),
]
