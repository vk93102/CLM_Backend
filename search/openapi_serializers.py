from rest_framework import serializers


class SearchHybridRequestSerializer(serializers.Serializer):
    query = serializers.CharField()
    limit = serializers.IntegerField(required=False, default=20)


class SearchAdvancedRequestSerializer(serializers.Serializer):
    query = serializers.CharField(required=False, allow_blank=True, default='')
    filters = serializers.DictField(required=False, default=dict)
    limit = serializers.IntegerField(required=False, default=20)


class SearchFacetedRequestSerializer(serializers.Serializer):
    query = serializers.CharField(required=False, allow_blank=True, default='')
    facet_filters = serializers.DictField(required=False, default=dict)
    limit = serializers.IntegerField(required=False, default=20)


class SearchIndexUpsertRequestSerializer(serializers.Serializer):
    entity_type = serializers.CharField()
    entity_id = serializers.CharField()
    title = serializers.CharField()
    content = serializers.CharField()
    keywords = serializers.ListField(child=serializers.CharField(), required=False, default=list)


class SearchSimilarByTextRequestSerializer(serializers.Serializer):
    text = serializers.CharField()
    limit = serializers.IntegerField(required=False, default=20)
    similarity_threshold = serializers.FloatField(required=False, default=0.6)
