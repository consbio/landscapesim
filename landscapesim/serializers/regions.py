import json

from rest_framework import serializers
from django.core.urlresolvers import reverse

from landscapesim.models import Region


class ReportingUnitSerializer(serializers.Serializer):
    type = serializers.SerializerMethodField()
    properties = serializers.SerializerMethodField()
    geometry = serializers.SerializerMethodField()

    class Meta:
        fields = ('type', 'geometry', 'properties',)

    def get_type(self, obj):
        return 'Feature'

    def get_geometry(self, obj):
        return json.loads(obj.polygon.json)

    def get_properties(self, obj):
        return {
            'id': obj.id,
            'unit_id': obj.unit_id,
            'name': obj.name
        }


class RegionSerializer(serializers.ModelSerializer):

    url = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = ('id', 'name', 'url')
    
    def get_url(self, obj):
        return reverse('region-reporting-units', args=[obj.id])
