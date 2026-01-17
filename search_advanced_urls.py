"""
Advanced Search API URLs Configuration
Registers all search endpoints
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from advanced_search import SearchViewSet, search_api_documentation

# Router for ViewSet endpoints
router = DefaultRouter()
router.register(r'', SearchViewSet, basename='search')

# URL patterns
urlpatterns = [
    path('documentation/', search_api_documentation, name='search-documentation'),
] + router.urls

# Include search endpoints
# - POST /api/search/full-text/
# - POST /api/search/semantic/
# - GET /api/search/similar/
# - POST /api/search/filtered/
# - POST /api/search/ocr-extract/
# - GET /api/search/documentation/
