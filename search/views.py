from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import SearchIndexModel
from .serializers import SearchIndexSerializer
from django.db.models import Q

class SearchViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def list(self, request):
        results = SearchIndexModel.objects.all()[:10]
        return Response(SearchIndexSerializer(results, many=True).data)
    
    @action(detail=False, methods=['get'])
    def semantic(self, request):
        query = request.query_params.get('q', '')
        results = SearchIndexModel.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )[:20]
        return Response({
            'query': query,
            'results': SearchIndexSerializer(results, many=True).data,
            'count': results.count()
        })
    
    @action(detail=False, methods=['get'])
    def hybrid(self, request):
        query = request.query_params.get('q', '')
        results = SearchIndexModel.objects.filter(
            Q(title__icontains=query) | Q(keywords__contains=[query])
        )[:20]
        return Response({
            'query': query,
            'results': SearchIndexSerializer(results, many=True).data
        })
    
    @action(detail=False, methods=['get'])
    def facets(self, request):
        facets = {
            'entity_types': SearchIndexModel.objects.values('entity_type').distinct().count(),
            'total_documents': SearchIndexModel.objects.count()
        }
        return Response(facets)
    
    @action(detail=False, methods=['post'])
    def advanced(self, request):
        query = request.data.get('query', '')
        filters = request.data.get('filters', {})
        results = SearchIndexModel.objects.filter(title__icontains=query)
        return Response(SearchIndexSerializer(results, many=True).data)
    
    @action(detail=False, methods=['get'])
    def suggestions(self, request):
        query = request.query_params.get('q', '')
        suggestions = SearchIndexModel.objects.filter(title__istartswith=query).values_list('title', flat=True).distinct()[:5]
        return Response({'suggestions': list(suggestions)})
