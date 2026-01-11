from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import SearchIndexModel
from .serializers import SearchIndexSerializer
from django.db.models import Q

class SearchListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        results = SearchIndexModel.objects.all()[:10]
        return Response(SearchIndexSerializer(results, many=True).data)

class SearchSemanticView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        results = SearchIndexModel.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )[:20]
        return Response({
            'query': query,
            'results': SearchIndexSerializer(results, many=True).data,
            'count': results.count()
        })

class SearchHybridView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        results = SearchIndexModel.objects.filter(
            Q(title__icontains=query)
        )[:20]
        return Response({
            'query': query,
            'results': SearchIndexSerializer(results, many=True).data
        })

class SearchFacetsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({
            'entity_types': SearchIndexModel.objects.values('entity_type').distinct().count(),
            'total_documents': SearchIndexModel.objects.count()
        })

class SearchAdvancedView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        query = request.data.get('query', '')
        results = SearchIndexModel.objects.filter(title__icontains=query)
        return Response(SearchIndexSerializer(results, many=True).data)

class SearchSuggestionsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        suggestions = SearchIndexModel.objects.filter(title__istartswith=query).values_list('title', flat=True).distinct()[:5]
        return Response({'suggestions': list(suggestions)})

urlpatterns = [
    path('search/', SearchListView.as_view(), name='search-list'),
    path('search/semantic/', SearchSemanticView.as_view(), name='search-semantic'),
    path('search/hybrid/', SearchHybridView.as_view(), name='search-hybrid'),
    path('search/facets/', SearchFacetsView.as_view(), name='search-facets'),
    path('search/advanced/', SearchAdvancedView.as_view(), name='search-advanced'),
    path('search/suggestions/', SearchSuggestionsView.as_view(), name='search-suggestions'),
]
